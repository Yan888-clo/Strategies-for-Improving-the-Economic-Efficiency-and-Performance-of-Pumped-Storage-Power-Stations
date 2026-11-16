/* Constant-head, equal-water-volume closed-cycle teaching model. No station calibration. */
(function(root){
function compute(s,v){
 const rho=1000,g=9.81,et=s.et/100,eg=s.eg/100,ep=s.ep/100,em=s.em/100;
 if(![s.h,s.lg,s.lp,s.qg,s.qp,s.et,s.eg,s.ep,s.em,v].every(Number.isFinite)||s.h<=0||s.lg<0||s.lp<0||s.lg>=s.h||s.qg<=0||s.qp<=0||v<=0||[s.et,s.eg,s.ep,s.em].some(x=>x<=0||x>100))throw new Error('参数超出物理有效范围');
 const hn=s.h-s.lg,hp=s.h+s.lp;
 const pGross=rho*g*s.qg*s.h/1e6,pWater=rho*g*s.qg*hn/1e6,pShaft=pWater*et,pGen=pShaft*eg;
 const pLift=rho*g*s.qp*s.h/1e6,pHyd=rho*g*s.qp*hp/1e6,pPump=pHyd/(ep*em);
 const etaGen=pGen/pGross,etaPump=pLift/pPump,eta=etaGen*etaPump;
 const tg=v/s.qg/3600,tp=v/s.qp/3600,eStore=rho*g*v*s.h/3.6e9,eGen=pGen*tg,ePump=pPump*tp;
 return {hn,hp,pGross,pWater,pShaft,pGen,pLift,pHyd,pPump,etaGen,etaPump,eta,tg,tp,eStore,eGen,ePump,eLoss:ePump-eGen};
}
function compare(a,b,target,price){if(!Number.isFinite(target)||target<=0||!Number.isFinite(price))throw new Error('统一任务或电价无效');const inputA=target/a.eta,inputB=target/b.eta,saving=inputA-inputB;return {points:(b.eta-a.eta)*100,relative:(b.eta/a.eta-1)*100,inputA,inputB,saving,savingRate:saving/inputA*100,costSaving:saving*1000*price};}
root.EfficiencyModel={compute,compare};if(typeof module!=='undefined')module.exports=root.EfficiencyModel;
})(typeof window==='undefined'?globalThis:window);
