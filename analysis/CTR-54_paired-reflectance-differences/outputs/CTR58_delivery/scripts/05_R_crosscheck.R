a <- commandArgs(TRUE)[1]
x <- read.csv(file.path(a,'tables/temporal_samples_for_R.csv')); expected<-read.csv(file.path(a,'tables/temporal_pixel_checks.csv'))
keys <- unique(x[c('band','row','col')]); out <- list()
for(i in seq_len(nrow(keys))) {
 k<-keys[i,]; v<-x$delta[x$band==k$band & x$row==k$row & x$col==k$col];v<-v[is.finite(v)]
 vals<-c(n=length(v),median=if(length(v)) median(v) else -9999,sd=if(length(v)>1) sd(v) else -9999)
 for(s in names(vals)) {
  e<-expected$actual[expected$band==k$band & expected$row==k$row & expected$col==k$col & expected$statistic==s]; stopifnot(length(e)==1,abs(vals[s]-e)<2e-7)
  out[[length(out)+1]]<-data.frame(k,statistic=s,R_value=unname(vals[s]),raster_value=e,absolute_error=abs(vals[s]-e))
 }
}
write.csv(do.call(rbind,out),file.path(a,'tables/R_temporal_crosscheck.csv'),row.names=FALSE)
cat('Independent base R temporal checks passed:',length(out),'\n')
