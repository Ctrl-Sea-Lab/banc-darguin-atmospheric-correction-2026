# Descriptive GAMs: acquisition is the temporal unit; pixels are not replicates.
args <- commandArgs(TRUE); A <- normalizePath(args[1]); F <- normalizePath(args[2])
suppressPackageStartupMessages(library(mgcv))
set.seed(56054)
d <- read.csv(file.path(A,'tables/date_band_summary.csv'), stringsAsFactors=FALSE)
d$date <- as.Date(d$date); origin <- min(d$date); d$t <- as.numeric(d$date-origin)
bands <- c('B2','B3','B4','B8'); stats <- c('median_delta','sd_delta')
stopifnot(nrow(d)==528, all(table(d$domain,d$band)==22), all(d$sd_delta>0))
write_table <- function(x,n) write.csv(x,file.path(A,'tables',paste0('ctr56_',n,'.csv')),row.names=FALSE,na='')
fit_one <- function(x,stat,k=5) {
 x$y <- if(stat=='sd_delta') log(x[[stat]]) else x[[stat]]
 gam(y~s(t,bs='cr',k=k),data=x,method='REML',family=gaussian())
}
inv <- function(z,stat) if(stat=='sd_delta') exp(z) else z
preds <- diags <- residuals_out <- contrasts <- influence <- sensitivity <- list(); models <- list(); warnings_out <- character()
withCallingHandlers({
for (domain in unique(d$domain)) for(b in bands) for(st in stats) {
 x <- d[d$domain==domain & d$band==b,];x <- x[order(x$t),]
 m <- fit_one(x,st); id <- paste(domain,b,st,sep=':'); models[[id]] <- m
 grid <- data.frame(t=seq(min(x$t),max(x$t),length.out=401))
 pr <- predict(m,grid,se.fit=TRUE,unconditional=TRUE)
 preds[[id]] <- data.frame(domain,band=b,statistic=st,date=origin+grid$t,t=grid$t,fit=inv(pr$fit,st),lower=inv(pr$fit-1.96*pr$se.fit,st),upper=inv(pr$fit+1.96*pr$se.fit,st),linear_predictor=pr$fit,se_linear_predictor=pr$se.fit)
 if(domain!='primary') next
 res <- residuals(m); kc <- k.check(m,n.rep=1000); big <- fit_one(x,st,10)
 bigpred <- inv(predict(big,grid),st); basepred <- inv(pr$fit,st)
 h <- m$hat; sigma <- sqrt(summary(m)$scale)
 diag <- data.frame(band=b,statistic=st,n=nrow(x),k=5,edf=summary(m)$s.table[1,'edf'],k_index=kc[1,3],k_p_value=kc[1,4],converged=m$converged,outer_convergence=m$outer.info$conv,rmse_model_scale=sqrt(mean(res^2)),adjacent_residual_correlation=cor(head(res,-1),tail(res,-1)),residual_abs_fitted_spearman=cor(abs(res),fitted(m),method='spearman'),shapiro_p=shapiro.test(res)$p.value,max_leverage=max(h),k10_edf=summary(big)$s.table[1,'edf'],k10_max_absolute_curve_change=max(abs(bigpred-basepred)),k10_reml_change=unname(big$gcv.ubre-m$gcv.ubre),smoothing_uncertainty_available=!is.null(m$Vc))
 diags[[id]] <- diag
 residuals_out[[id]] <- data.frame(band=b,statistic=st,date=x$date,t=x$t,observed=x[[st]],fitted=inv(fitted(m),st),residual_model_scale=res,standardized_residual=res/(sigma*sqrt(1-h)),leverage=h,coverage=x$coverage_fraction,sensor=x$sensor,flags_available=x$flags_available)
 # Endpoint contrast uses full coefficient covariance; log-SD contrasts become ratios.
 ep <- data.frame(t=range(x$t)); X <- predict(m,ep,type='lpmatrix'); L<-X[2,]-X[1,]
 V <- if(is.null(m$Vc)) m$Vp else m$Vc
 est <- drop(L%*%coef(m)); se<-sqrt(drop(L%*%V%*%L))
 contrasts[[id]] <- data.frame(band=b,statistic=st,contrast=if(st=='sd_delta') 'last/first typical SD ratio' else 'last-first fitted spatial median',estimate=inv(est,st),lower=inv(est-1.96*se,st),upper=inv(est+1.96*se,st),start=origin+min(x$t),end=origin+max(x$t))
 for(i in seq_len(nrow(x))) {
  xx<-x[-i,]; mm<-fit_one(xx,st); inside<-grid$t>=min(xx$t)&grid$t<=max(xx$t)
  change<-abs(inv(predict(mm,grid[inside,,drop=FALSE]),st)-basepred[inside])
  influence[[paste(id,i)]]<-data.frame(band=b,statistic=st,omitted_date=x$date[i],max_curve_change=max(change),rms_curve_change=sqrt(mean(change^2)),compared_start=origin+min(grid$t[inside]),compared_end=origin+max(grid$t[inside]))
 }
 # Missing-quality sensitivity and temporal/coverage association are diagnostic only.
 xx<-x[x$flags_available=='True',]; mm<-fit_one(xx,st); inside<-grid$t<=max(xx$t)
 sensitivity[[id]]<-data.frame(band=b,statistic=st,coverage_observed_spearman=cor(x$coverage_fraction,x[[st]],method='spearman'),coverage_residual_spearman=cor(x$coverage_fraction,res,method='spearman'),no_missing_flags_max_curve_change=max(abs(inv(predict(mm,grid[inside,,drop=FALSE]),st)-basepred[inside])),no_missing_flags_n=nrow(xx))
 preds[[paste0(id,':flags')]]<-data.frame(domain='flags_available_only',band=b,statistic=st,date=origin+grid$t[inside],t=grid$t[inside],fit=inv(predict(mm,grid[inside,,drop=FALSE]),st),lower=NA,upper=NA,linear_predictor=as.numeric(predict(mm,grid[inside,,drop=FALSE])),se_linear_predictor=NA)
}
},warning=function(w){warnings_out<<-c(warnings_out,conditionMessage(w));invokeRestart('muffleWarning')})
P<-do.call(rbind,preds); D<-do.call(rbind,diags); RES<-do.call(rbind,residuals_out); I<-do.call(rbind,influence)
write_table(P,'predictions');write_table(D,'diagnostics');write_table(RES,'residuals');write_table(do.call(rbind,contrasts),'endpoint_contrasts');write_table(I,'leave_one_date_out');write_table(do.call(rbind,sensitivity),'quality_coverage_diagnostics')
sens <- list(); observed <- list()
for(b in bands) for(st in stats) {
 p<-P[P$domain=='primary' & P$band==b & P$statistic==st,]
 x<-d[d$domain=='primary' & d$band==b,];x<-x[order(x$t),]
 observed[[paste(b,st)]]<-data.frame(band=b,statistic=st,n_dates=nrow(x),min=min(x[[st]]),max=max(x[[st]]),median_across_dates=median(x[[st]]),n_negative=sum(x[[st]]<0))
 for(dom in setdiff(unique(d$domain),'primary')) {
  q<-P[P$domain==dom & P$band==b & P$statistic==st,]
  y<-d[d$domain==dom & d$band==b,];y<-y[order(y$t),]
  sens[[paste(b,st,dom)]]<-data.frame(band=b,statistic=st,domain=dom,min_pixels=min(y$n_valid),max_pixels=max(y$n_valid),observed_max_change=max(abs(y[[st]]-x[[st]])),observed_median_change=median(y[[st]]-x[[st]]),observed_correlation=cor(x[[st]],y[[st]]),curve_max_change=max(abs(q$fit-p$fit)),curve_rms_change=sqrt(mean((q$fit-p$fit)^2)))
 }
}
write_table(do.call(rbind,sens),'domain_sensitivity');write_table(do.call(rbind,observed),'observed_summary')
write_table(unique(d[d$domain=='primary' & d$band=='B2',c('date','t','sensor','flags_available','coverage_fraction')]),'date_design')
# Irregular-time residual dependence: empirical semivariances on actual day lags.
vg<-list()
for(b in bands) for(st in stats) {
 x<-RES[RES$band==b & RES$statistic==st,]; ij<-combn(nrow(x),2);lags<-abs(x$t[ij[1,]]-x$t[ij[2,]])
 v<-(x$residual_model_scale[ij[1,]]-x$residual_model_scale[ij[2,]])^2/2
 bins<-cut(lags,c(0,15,30,60,120,240,500),include.lowest=TRUE)
 for(bin in levels(bins)) if(any(bins==bin)) vg[[paste(b,st,bin)]]<-data.frame(band=b,statistic=st,lag_bin_days=bin,n_pairs=sum(bins==bin),mean_semivariance=mean(v[bins==bin]),residual_variance=var(x$residual_model_scale))
}
write_table(do.call(rbind,vg),'residual_variogram')
saveRDS(models,file.path(A,'outputs/ctr56_gam_models.rds'),compress='xz')
writeLines(unique(warnings_out),file.path(A,'provenance/ctr56_model_warnings.txt'))
capture.output(sessionInfo(),file=file.path(A,'provenance/ctr56_R_session.txt'))
cols<-c(B2='#0072B2',B3='#009E73',B4='#D55E00',B8='#CC79A7'); shapes<-c(16,17,15,18)
ticks<-as.Date(c('2025-01-01','2025-04-01','2025-07-01','2025-10-01','2026-01-01','2026-04-01'))
# Main figure shows all 88 date/band values in each panel; no extrapolation or clipping.
draw_main<-function() {
 layout(matrix(1:2,2,1));par(mar=c(2.6,5.1,1.3,1),oma=c(1,0,1.3,0),mgp=c(2.7,.7,0),tcl=-.25,cex=.95)
 for(st in stats) {
  x<-d[d$domain=='primary',];p<-P[P$domain=='primary' & P$statistic==st,]
  plot(range(x$date),range(c(x[[st]],p$fit)),type='n',xaxt='n',xlab='',ylab=if(st=='median_delta') expression('Spatial median '*Delta*R) else expression('Spatial SD of '*Delta*R),bty='l')
  axis.Date(1,at=ticks,format='%b %Y');abline(h=pretty(range(x[[st]])),col='#EEEEEE');if(st=='median_delta')abline(h=0,col='#888888',lty=3)
  for(j in seq_along(bands)) {b<-bands[j];z<-p[p$band==b,];lines(z$date,z$fit,col=cols[b],lwd=2);z<-x[x$band==b,];points(z$date,z[[st]],col=cols[b],pch=shapes[j],cex=.78)}
  if(st=='median_delta') legend('bottomright',legend=bands,col=cols,pch=shapes,lty=1,lwd=2,horiz=TRUE,bty='n',cex=.9)
 }
 mtext('Acquisition date',side=1,outer=TRUE,line=0)
}
png(file.path(F,'ctr56_temporal_gam.png'),width=8.6,height=6.2,units='in',res=360,type='cairo');draw_main();dev.off()
pdf(file.path(F,'ctr56_temporal_gam.pdf'),width=8.6,height=6.2,useDingbats=FALSE);draw_main();dev.off()
# Uncertainty and complete-date sensitivity, kept out of the minimal main graphic.
png(file.path(F,'ctr56_uncertainty_coverage.png'),width=12,height=6,units='in',res=220,type='cairo')
par(mfrow=c(2,4),mar=c(3,3.6,2.2,.5),mgp=c(2.2,.65,0),cex=.8)
for(st in stats) for(b in bands) {
 p<-P[P$domain=='primary' & P$band==b & P$statistic==st,];q<-P[P$domain=='complete_dates' & P$band==b & P$statistic==st,];x<-d[d$domain=='primary' & d$band==b,]
 plot(range(p$date),range(c(p$lower,p$upper,q$fit,x[[st]])),type='n',xaxt='n',xlab='',ylab=if(st=='median_delta') 'Spatial median delta R' else 'Spatial SD of delta R',main=b,bty='l')
 axis.Date(1,at=ticks[c(1,3,5)],format='%b %Y');polygon(c(p$date,rev(p$date)),c(p$lower,rev(p$upper)),col=adjustcolor(cols[b],alpha.f=.15),border=NA)
 lines(p$date,p$fit,col=cols[b],lwd=2);lines(q$date,q$fit,lty=2,lwd=1.7);points(x$date,x[[st]],pch=16,col=cols[b],cex=.55)
 if(st=='median_delta' && b=='B2')legend('bottomright',c('Primary','Fixed core'),col=c(cols[b],'black'),lty=c(1,2),bty='n',cex=.8)
};dev.off()
png(file.path(F,'ctr56_residual_diagnostics.png'),width=12,height=8,units='in',res=160,type='cairo')
par(mfrow=c(4,4),mar=c(3,3,2,.5),mgp=c(1.8,.6,0),cex=.75)
for(st in stats) {
 for(b in bands) {x<-RES[RES$band==b & RES$statistic==st,];plot(x$date,x$standardized_residual,pch=16,col=cols[b],xlab='',ylab='Standardized residual',main=paste(b,st),bty='l');abline(h=0,lty=3)}
 for(b in bands) {x<-RES[RES$band==b & RES$statistic==st,];qqnorm(x$standardized_residual,main=paste(b,'QQ'),pch=16,col=cols[b]);qqline(x$standardized_residual)}
};dev.off()
print(D);print(do.call(rbind,contrasts));print(do.call(rbind,sens)[do.call(rbind,sens)$domain=='complete_dates',])
