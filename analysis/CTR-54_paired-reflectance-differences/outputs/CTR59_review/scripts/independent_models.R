args<-commandArgs(TRUE);A<-normalizePath(args[1]);O<-normalizePath(args[2]);library(mgcv)
x<-read.csv(file.path(A,'tables/date_band_summary.csv'));x$date<-as.Date(x$date);x$t<-as.numeric(x$date-min(x$date))
pred<-read.csv(file.path(A,'tables/ctr56_predictions.csv'));con<-read.csv(file.path(A,'tables/ctr56_endpoint_contrasts.csv'));out<-list()
for(b in c('B2','B3','B4','B8'))for(st in c('median_delta','sd_delta')){
 d<-x[x$domain=='primary'&x$band==b,];d<-d[order(d$t),];d$y<-if(st=='sd_delta')log(d[[st]])else d[[st]]
 fit<-gam(y~s(t,k=5,bs='cr'),method='REML',data=d)
 pp<-pred[pred$domain=='primary'&pred$band==b&pred$statistic==st,];Xp<-predict(fit,data.frame(t=pp$t),type='lpmatrix');V<-vcov(fit,unconditional=TRUE)
 eta<-drop(Xp%*%coef(fit));se<-sqrt(rowSums((Xp%*%V)*Xp));inv<-if(st=='sd_delta')exp else identity
 error<-max(abs(c(inv(eta)-pp$fit,inv(eta-1.96*se)-pp$lower,inv(eta+1.96*se)-pp$upper)))
 cc<-con[con$band==b&con$statistic==st,];L<-Xp[nrow(Xp),]-Xp[1,];est<-sum(L*coef(fit));s<-sqrt(drop(L%*%V%*%L));contrast_error<-max(abs(c(inv(est)-cc$estimate,inv(est-1.96*s)-cc$lower,inv(est+1.96*s)-cc$upper)))
 stopifnot(error<1e-10,contrast_error<1e-10,nrow(d)==22,nrow(pp)==401,all(diff(pp$t)>0))
 out[[paste(b,st)]]<-data.frame(band=b,statistic=st,n=22,predictions=401,max_curve_interval_error=error,max_endpoint_error=contrast_error,edf=sum(fit$edf)-1,converged=fit$converged)
}
# Execute the exact palette definition without loading/running the plotting script.
cmap<-colorRampPalette(c('#2166AC','#FFFFFF','#B2182B'))(257)
z<-c(0,.01,.02,.03);idx<-1+floor(pmax(0,pmin(1,z/.02))*256+.5)
stopifnot(identical(toupper(cmap[idx]),c('#2166AC','#FFFFFF','#B2182B','#B2182B')))
write.csv(data.frame(sd=z,index=idx,hex=cmap[idx]),file.path(O,'tables/independent_colors.csv'),row.names=FALSE)
write.csv(do.call(rbind,out),file.path(O,'tables/independent_models.csv'),row.names=FALSE)
capture.output(sessionInfo(),file=file.path(O,'provenance/R_session.txt'));print(do.call(rbind,out));cat('PASS: primary GAM curves, covariance intervals, contrasts and palette anchors\n')
