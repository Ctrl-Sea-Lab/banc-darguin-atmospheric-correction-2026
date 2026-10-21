# Independent arithmetic verification from frozen wide inputs, using base R only.
p <- 'analysis/CTR-24_data-dictionary'
read <- function(name) {
  z <- read.csv(file.path(p, 'tables', name), na.strings='NA', check.names=FALSE)
  for (k in intersect(c('common_finite_triple','included_validation_pair'), names(z))) {
    stopifnot(all(z[[k]] %in% c('True','False')))
    z[[k]] <- z[[k]] == 'True'
  }
  z
}
x <- read('ctr36_station_inputs.csv')
primary <- read('ctr37_station_metrics.csv')
v5 <- read('ctr37_v5_sensitivity_metrics.csv')
checks <- character()
check <- function(name, ok) {
  if (!isTRUE(ok)) stop(name)
  checks <<- c(checks, name)
}
calc <- function(e) {
  if (!length(e)) return(c(bias=NA_real_, MAE=NA_real_, RMSE=NA_real_))
  c(bias=mean(e), MAE=mean(abs(e)), RMSE=sqrt(mean(e^2)))
}
check('known mixed-sign fixture detects cancellation', isTRUE(all.equal(unname(calc(c(-2,1,4))), c(1,7/3,sqrt(7)))))
check('zero-error fixture', all(calc(c(0,0,0)) == 0))
check('empty input yields NA metrics', all(is.na(calc(numeric(0)))))
for (role in c('v4_primary','v5_sensitivity')) {
  out <- if (role == 'v4_primary') primary else v5[v5$population == 'primary',]
  ref <- if (role == 'v4_primary') 'ASD_v4' else 'ASD_v5_sensitivity'
  for (sid in unique(x$station_id)) {
    z <- x[x$station_id == sid,]
    common <- is.finite(z[[ref]]) & is.finite(z$L2A) & is.finite(z$ACOLITE)
    for (method in c('L2A','ACOLITE')) {
      m <- out[out$station_id == sid & out$correction == method,]
      expected <- calc(z[[method]][common] - z[[ref]][common])
      actual <- unlist(m[c('bias','MAE','RMSE')], use.names=FALSE)
      check(paste(role,sid,method,'independent arithmetic and denominator'), nrow(m)==1 && m$n_paired_bands==sum(common) && max(abs(expected-actual)) < 1e-14)
      check(paste(role,sid,method,'inequalities'), m$RMSE+1e-14>=m$MAE && m$MAE+1e-14>=abs(m$bias))
    }
  }
}
for (file in c('ctr37_figure_pairs.csv','ctr37_v5_sensitivity_pairs.csv')) {
  z <- read(file)
  check(paste(file,'unique keys'), !anyDuplicated(z[c('station_id','band_id','correction')]))
  check(paste(file,'78 rows; 36 finite correction rows'), nrow(z)==78 && sum(z$common_finite_triple)==36)
  good <- z[z$common_finite_triple,]
  check(paste(file,'signed differences'), max(abs(good$signed_difference-(good$satellite_reflectance-good$ASD_reflectance)))<1e-14)
  for (method in c('L2A','ACOLITE')) {
    r <- good[good$correction==method,]
    j <- match(paste(r$station_id,r$band_id),paste(x$station_id,x$band_id))
    ref <- if(file=='ctr37_figure_pairs.csv') 'ASD_v4' else 'ASD_v5_sensitivity'
    check(paste(file,method,'exact figure input values'), all(r$satellite_reflectance==x[[method]][j]) && all(r$ASD_reflectance==x[[ref]][j]))
  }
  check(paste(file,'missing values remain NA'), all(is.na(z$satellite_reflectance[!z$common_finite_triple])) && all(is.na(z$ASD_reflectance[!z$common_finite_triple])) && all(is.na(z$signed_difference[!z$common_finite_triple])))
  check(paste(file,'both methods have identical keys'), identical(with(good[good$correction=='L2A',],paste(station_id,band_id)),with(good[good$correction=='ACOLITE',],paste(station_id,band_id))))
  check(paste(file,'no physical hold released'), !any(z$included_validation_pair))
}
s <- read('ctr37_supplementary_metrics.csv')
check('seven supplementary stations each correction with N=0 and NA metrics', nrow(s)==14 && all(s$n_paired_bands==0) && all(is.na(as.matrix(s[c('bias','MAE','RMSE')]))))
check('original eligible validation table is empty', nrow(read('ctr34_eligible_pairs.csv'))==0)
check('AC06 cancellation sign retained', primary$bias[primary$station_id=='AC06' & primary$correction=='ACOLITE'] < 0)
check('PI-excluded stations absent', !any(c('AC03','AC04') %in% primary$station_id))
check('unitless reflectance units', all(primary$unit==1))
for(file in c('ctr37_spectral_long.csv','ctr37_v5_spectral_long.csv')) {
  z <- read(file)
  check(paste(file,'unique keys and finite counts'), nrow(z)==117 && !anyDuplicated(z[c('station_id','band_id','series')]) && sum(is.finite(z$reflectance))==54)
}
writeLines(c(paste(length(checks),'independent R numerical checks passed'), checks, capture.output(sessionInfo())),file.path(p,'provenance/ctr37_independent_arithmetic.txt'))
cat(length(checks),'independent R numerical checks passed\n')
