args<-commandArgs(TRUE);A<-normalizePath(args[1]);suppressPackageStartupMessages(library(mgcv))
m<-readRDS(file.path(A,'outputs/ctr56_gam_models.rds'))
p<-read.csv(file.path(A,'tables/ctr56_predictions.csv'));d<-read.csv(file.path(A,'tables/date_band_summary.csv'))
i<-read.csv(file.path(A,'tables/ctr56_leave_one_date_out.csv'));c<-read.csv(file.path(A,'tables/ctr56_endpoint_contrasts.csv'))
stopifnot(length(m)==48,nrow(i)==176,all(vapply(m,function(x)isTRUE(x$converged),logical(1))),all(p$fit[p$statistic=='sd_delta']>0))
errors<-numeric();ols_errors<-numeric()
for(id in names(m)) {
 keys<-strsplit(id,':',fixed=TRUE)[[1]];mm<-m[[id]]
 pp<-p[p$domain==keys[1] & p$band==keys[2] & p$statistic==keys[3],]
 stopifnot(nrow(pp)==401,all(pp$t>=0),all(pp$t<=445),all(pp$lower<=pp$fit),all(pp$upper>=pp$fit))
 pr<-predict(mm,data.frame(t=pp$t),se.fit=TRUE,unconditional=TRUE)
 errors<-c(errors,max(abs(pr$fit-pp$linear_predictor)),max(abs(pr$se.fit-pp$se_linear_predictor)))
 response<-if(keys[3]=='sd_delta')exp(pr$fit) else pr$fit
 stopifnot(max(abs(response-pp$fit))<1e-10)
 if(keys[1]=='primary') {
  x<-d[d$domain=='primary' & d$band==keys[2],];x$t<-as.numeric(as.Date(x$date)-as.Date('2025-01-06'))
  if(keys[3]=='median_delta') {
   ols<-lm(median_delta~t,data=x);err<-max(abs(predict(ols,data.frame(t=pp$t))-pp$fit));stopifnot(err<2e-6);ols_errors<-c(ols_errors,err)
  }
  cc<-c[c$band==keys[2] & c$statistic==keys[3],]
  L<-predict(mm,data.frame(t=c(0,445)),type='lpmatrix');z<-L[2,]-L[1,];e<-sum(z*coef(mm));se<-sqrt(sum(z*(mm$Vc%*%z)))
  vals<-c(e,e-1.96*se,e+1.96*se);if(keys[3]=='sd_delta') vals<-exp(vals)
  stopifnot(max(abs(vals-as.numeric(cc[,c('estimate','lower','upper')])))<1e-10)
 }
}
stopifnot(max(errors)<1e-10)
cat('PASS: 48 converged models; 401 in-range predictions per model; positive inverse-transformed SD; prediction/covariance and endpoint-contrast agreement; 176 influence refits.\n')
cat('Maximum saved prediction/SE discrepancy:',max(errors),'\nMaximum linear-GAM versus independent OLS discrepancy:',max(ols_errors),'\n')
