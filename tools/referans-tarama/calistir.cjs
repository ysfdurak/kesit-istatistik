global.window=global;const path=require('path'),D=path.join(__dirname,'../../docs/');require(D+'math.js');require(D+'analysis-engine.js');const E=AnalysisEngine,S=Stats;
const C=require(path.join(__dirname,'cases.json')),out=[];
for(const c of C){let r;try{switch(c.kind){
case 'normalCDF':r=E.normalCDF(c.x);break;case 'normalInv':r=E.normalInv(c.p);break;case 'tP':r=E.tP(c.t,c.df);break;case 'tInv':r=E.tInv(c.p,c.df);break;
case 'gammaQ':r=E.gammaQ(c.a,c.x);break;case 'betaI':r=E.betaI(c.x,c.a,c.b);break;case 'ci':r=E.ci(c.a,c.level);break;case 'ttest1':r=E.ttest(c.a,null,c.mu);break;
case 'welch':r=E.ttest(c.a,c.b);break;case 'paired':r=E.ttest(c.a,c.b,0,true);break;case 'wilson':r=E.wilson(c.k,c.n);break;case 'ab':r=E.ab(c.k1,c.n1,c.k2,c.n2);break;
case 'anova':r=E.anova(c.groups);break;case 'categorical':r=E.categorical(c.t);break;case 'pearson':r=E.correlation(c.x,c.y);break;case 'spearman':r=E.correlation(c.x,c.y,true);break;
case 'regression':r=E.regression(c.x,c.y);delete r.pred;delete r.res;break;case 'mannWhitney':r=E.mannWhitney(c.a,c.b);break;case 'bayes':r=E.bayes(c.k,c.n,c.a,c.b);break;
case 'metrics':r=E.metrics(c.y,c.p);delete r.roc;delete r.pr;break;case 'summary':r=S.summary(c.a);break;case 'survival':r=E.survival(c.time,c.event);delete r.steps;break;case 'binomial':r=S.binomial(c.n,c.p,c.k);break;}
out.push({ok:true,r})}catch(e){out.push({ok:false,err:String(e.message)})}}
require('fs').writeFileSync(path.join(__dirname,'js.json'),JSON.stringify(out));
