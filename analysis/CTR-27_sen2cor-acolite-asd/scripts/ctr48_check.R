# Independent base-R arithmetic from Roger's long table; no extraction imports.
# Run from project root through scripts/project-env.sh to activate renv.
p <- 'analysis/CTR-27_sen2cor-acolite-asd'
options(digits=17)
s <- read.csv(file.path(p,'tables/ctr47_satellite.csv'),check.names=FALSE)
bands <- c('B01','B02','B03','B04','B05','B06','B07','B08','B8A')
keys <- c('target_id','band_id')
a <- s[s$correction=='ACOLITE',c(keys,'reflectance')]
b <- s[s$correction=='Sen2Cor',c(keys,'reflectance')]
z <- merge(b,a,by=keys,suffixes=c('_S','_A'))
stopifnot(nrow(z)==54L,all(is.finite(z$reflectance_S)),all(is.finite(z$reflectance_A)))
z$delta <- z$reflectance_S-z$reflectance_A
v <- read.csv(file.path(p,'tables/ctr48_pairs.csv'),check.names=FALSE)
j <- merge(z,v,by=keys)
errors <- c(pair=max(abs(j$delta-j$Sen2Cor_minus_ACOLITE)))
calc <- function(x) c(n_pairs=length(x),mean_signed=mean(x),median_signed=median(x),
                     mean_absolute_difference=mean(abs(x)),min_signed=min(x),max_signed=max(x),
                     n_positive=sum(x>0),n_negative=sum(x<0),n_zero=sum(x==0))
for (axis in c('target','band')) {
  key <- paste0(axis,'_id'); lev <- if(axis=='band') bands else sort(unique(z[[key]]))
  ans <- as.data.frame(do.call(rbind,lapply(lev,function(id)calc(z$delta[z[[key]]==id]))))
  ans[[key]] <- lev
  expected <- read.csv(file.path(p,paste0('tables/ctr48_',axis,'_summary.csv')))
  expected <- expected[match(lev,expected[[key]]),]
  for(n in names(calc(z$delta))) errors[paste(axis,n,sep='_')] <- max(abs(ans[[n]]-expected[[n]]))
}
# All adjacent differences are independently formed from source reflectances.
steps <- read.csv(file.path(p,'tables/ctr48_spectral_steps.csv'))
for(i in seq_len(nrow(steps))) {
  r <- steps[i,]; prev <- z[z$target_id==r$target_id & z$band_id==r$from_band,]
  nextrow <- z[z$target_id==r$target_id & z$band_id==r$to_band,]
  sd <- nextrow$reflectance_S-prev$reflectance_S; ad <- nextrow$reflectance_A-prev$reflectance_A
  stopifnot(abs(sd-r$Sen2Cor_step)<1e-14,abs(ad-r$ACOLITE_step)<1e-14,
            abs((sd-ad)-r$step_difference)<1e-14,(sign(sd)==sign(ad))==(r$same_direction=="True"))
}
stopifnot(max(errors)<1e-14)
# Decimal CSV parsing may differ below 1e-14; this is numeric tolerance, not uncertainty.
write.csv(data.frame(check=names(errors),max_absolute_difference=as.numeric(errors),
                     tolerance=1e-14,passed=errors<1e-14),file.path(p,'tables/ctr48_R_crosscheck.csv'),row.names=FALSE)
capture.output({cat('PASS: independent R join, 54 differences, target/band summaries and 48 spectral steps.\n')
                print(errors);cat('\nPooled descriptive values, not independent-replicate estimates:\n');print(calc(z$delta));sessionInfo()},
               file=file.path(p,'provenance/ctr48_R_validation.txt'))
cat('PASS: independent R numerical checks. Maximum discrepancy:',max(errors),'\n')

logfile <- file.path(p,"provenance/ctr48_R_validation.txt")
writeLines(sub("[[:space:]]+$", "", readLines(logfile)), logfile)
