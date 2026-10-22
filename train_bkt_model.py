import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score, accuracy_score
BASE=Path(__file__).resolve().parent
INPUT=BASE / 'Generated_Learner_Assessment.xlsx'; OUT=BASE / 'bkt_model_outputs'; OUT.mkdir(exist_ok=True)
SEED=42; THRESHOLD=.80
cols=['student_id','question_id','skill_id','correct','attempt_number','response_time','hint_used','difficulty','course_id','answer_attempt','problem_type']
df=pd.read_excel(INPUT,sheet_name='Synthetic')[cols].copy()
for c in ['correct','attempt_number','response_time','hint_used']: df[c]=pd.to_numeric(df[c],errors='coerce')
df['hint_used']=df.hint_used.fillna(0); df=df.dropna(subset=['student_id','skill_id','correct','attempt_number']); df=df[df.correct.isin([0,1])].copy(); df['correct']=df.correct.astype(int); df['student_id']=df.student_id.astype(str); df['skill_id']=df.skill_id.astype(str); df['_order']=np.arange(len(df)); df=df.sort_values(['student_id','skill_id','attempt_number','_order']).reset_index(drop=True)
# The uploaded workbook has repeated rows for the same student-skill-attempt number.
# Collapse these to one observation per attempt so BKT does not count duplicate rows as learning transitions.
agg = {'correct':'mean','response_time':'mean','hint_used':'mean','question_id':'first','difficulty':'first','course_id':'first','answer_attempt':'max','problem_type':'first','_order':'min'}
df = df.groupby(['student_id','skill_id','attempt_number'], as_index=False, sort=False).agg(agg)
df['correct'] = (df['correct'] >= 0.5).astype(int)
df=df.sort_values(['student_id','skill_id','attempt_number','_order']).reset_index(drop=True)
train_ids,test_ids=train_test_split(df.student_id.unique(),test_size=.2,random_state=SEED); train=df[df.student_id.isin(train_ids)]; test=df[df.student_id.isin(test_ids)]
def pack_sequences(seqs):
    n=len(seqs); m=max(map(len,seqs)); y=np.zeros((n,m),dtype=float); mask=np.zeros((n,m),dtype=float)
    for i,s in enumerate(seqs): y[i,:len(s)]=s; mask[i,:len(s)]=1
    return y,mask
def fit_skill(seqs):
    y,mask=pack_sequences(seqs)
    def nll(p):
        l0,learn,guess,slip=p; mastery=np.full(y.shape[0],l0); total=0.
        for t in range(y.shape[1]):
            active=mask[:,t]; pc=np.clip(mastery*(1-slip)+(1-mastery)*guess,1e-10,1-1e-10)
            total -= np.sum(active*(y[:,t]*np.log(pc)+(1-y[:,t])*np.log(1-pc)))
            updated=np.where(y[:,t] == 1, mastery*(1-slip)/pc, mastery*slip/(1-pc))
            mastery=np.where(active,updated+(1-updated)*learn,mastery)
        return float(total)
    starts=[[.25,.15,.20,.10],[.50,.10,.15,.05]]; bounds=[(.001,.999),(.001,.80),(.001,.40),(.001,.40)]; best=None
    for st in starts:
        r=minimize(nll,st,method='L-BFGS-B',bounds=bounds,options={'maxiter':250,'ftol':1e-8})
        if r.success and (best is None or r.fun<best.fun): best=r
    if best is None: best=minimize(nll,starts[0],method='L-BFGS-B',bounds=bounds,options={'maxiter':400})
    a,b,c,d=best.x
    return {'initial_mastery':float(a),'learn_probability':float(b),'guess_probability':float(c),'slip_probability':float(d),'train_negative_log_likelihood':float(best.fun),'optimizer_success':bool(best.success)}
def trace(obs,p):
    mastery=p['initial_mastery']; pred=[]; post=[]
    for y in obs:
        pc=float(np.clip(mastery*(1-p['slip_probability'])+(1-mastery)*p['guess_probability'],1e-8,1-1e-8)); pred.append(pc)
        mastery=mastery*(1-p['slip_probability'])/pc if y==1 else mastery*p['slip_probability']/(1-pc); post.append(mastery); mastery += (1-mastery)*p['learn_probability']
    return np.asarray(pred),np.asarray(post)
models={}
for skill,part in train.groupby('skill_id'):
    seqs=[g.correct.to_numpy(dtype=int) for _,g in part.groupby('student_id',sort=False)]
    models[skill]=fit_skill(seqs)
actual=[]; probs=[]
for skill,part in test.groupby('skill_id'):
    for _,g in part.groupby('student_id',sort=False):
        y=g.correct.to_numpy(dtype=int); pr,_=trace(y,models[skill]); actual.extend(y); probs.extend(pr)
actual=np.asarray(actual); probs=np.asarray(probs)
metrics={'split':'80% train learners / 20% held-out test learners','random_seed':SEED,'train_students':int(len(train_ids)),'test_students':int(len(test_ids)),'train_rows':int(len(train)),'test_rows':int(len(test)),'test_log_loss':float(log_loss(actual,probs,labels=[0,1])),'test_brier_score':float(brier_score_loss(actual,probs)),'test_auc':float(roc_auc_score(actual,probs)),'test_accuracy_at_0_5':float(accuracy_score(actual,(probs>=.5).astype(int))),'note':'Predictions are made before each held-out response and then the BKT state is updated. Duplicate student-skill-attempt rows are aggregated. No timestamp is present; attempt_number orders observations.'}
rows=[]
for (student,skill),g in df.groupby(['student_id','skill_id'],sort=False):
    g=g.sort_values(['attempt_number','_order']); p=models[skill]; y=g.correct.to_numpy(dtype=int); _,post=trace(y,p); m=float(post[-1]); recent=g.tail(3); rt=recent.response_time.mean(); hr=recent.hint_used.mean(); acc=recent.correct.mean(); last=recent.iloc[-1]
    if m>=THRESHOLD: status='Mastered'; rec='Advanced problems or next skill; verify with a harder assessment.'
    elif m<.5:
        status='High-priority gap'; rec='Guided tutorial and worked examples, followed by scaffolded practice.' if hr>=.34 else ('Foundational revision and short exercises.' if pd.notna(rt) and rt>90 else 'Review core concepts and practise easy questions with feedback.')
    else:
        status='Developing'; rec='Hint-supported practice, gradually fading hints.' if hr>=.34 else ('Worked examples and timed exercises.' if pd.notna(rt) and rt>90 else ('Targeted practice and review incorrect answers.' if acc<.67 else 'Medium-difficulty practice and a mastery-check quiz.'))
    rows.append({'student_id':student,'skill_id':skill,'course_id':last.course_id,'attempts_observed':len(g),'recent_accuracy_3':round(float(acc),4),'mastery_probability':round(m,6),'mastery_percent':round(m*100,2),'skill_status':status,'recent_mean_response_time':round(float(rt),2) if pd.notna(rt) else np.nan,'recent_hint_rate':round(float(hr),4) if pd.notna(hr) else np.nan,'recommendation':rec})
mastery=pd.DataFrame(rows).sort_values(['student_id','mastery_probability'])
gaps=mastery.groupby(['skill_id'],as_index=False).agg(learners=('student_id','nunique'),mean_mastery=('mastery_probability','mean'),median_mastery=('mastery_probability','median'),pct_below_80=('mastery_probability',lambda x:float((x<.8).mean()*100)),pct_below_50=('mastery_probability',lambda x:float((x<.5).mean()*100)))
gaps['mean_mastery_percent']=(gaps.mean_mastery*100).round(2); gaps['pct_below_80']=gaps.pct_below_80.round(2); gaps['pct_below_50']=gaps.pct_below_50.round(2); gaps=gaps.sort_values('mean_mastery')
params=pd.DataFrame.from_dict(models,orient='index').rename_axis('skill_id').reset_index(); params['course_id']=params.skill_id.map(train.groupby('skill_id').course_id.agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]))
profile=pd.DataFrame([['Rows used',len(df)],['Unique students',df.student_id.nunique()],['Unique skills',df.skill_id.nunique()],['Unique question IDs',df.question_id.nunique()],['Overall correct rate (%)',round(df.correct.mean()*100,2)],['Duplicate student-skill-attempt combinations after aggregation',int(df.duplicated(['student_id','skill_id','attempt_number']).sum())],['Ordering note','Repeated student-skill-attempt rows are aggregated; no timestamp exists, so attempt_number orders observations.']],columns=['item','value'])
mastery.to_csv(OUT/'learner_skill_mastery.csv',index=False); gaps.to_csv(OUT/'skill_gap_summary.csv',index=False); params.to_csv(OUT/'bkt_skill_parameters.csv',index=False)
with open(OUT/'evaluation_metrics.json','w') as f: json.dump(metrics,f,indent=2)
with open(OUT/'bkt_skill_parameters.json','w') as f: json.dump(models,f,indent=2)
with pd.ExcelWriter(OUT/'bkt_analysis_report.xlsx',engine='openpyxl') as w:
    profile.to_excel(w,index=False,sheet_name='Dataset_Profile'); params.to_excel(w,index=False,sheet_name='BKT_Parameters'); gaps.to_excel(w,index=False,sheet_name='Skill_Gap_Summary'); mastery.to_excel(w,index=False,sheet_name='Learner_Mastery'); pd.DataFrame([metrics]).to_excel(w,index=False,sheet_name='Evaluation')
print(json.dumps(metrics,indent=2)); print('\nGAP SUMMARY\n'+gaps.to_string(index=False)); print('\nPARAMETERS\n'+params.to_string(index=False)); print('\nOUTPUTS', [x.name for x in OUT.iterdir()])
