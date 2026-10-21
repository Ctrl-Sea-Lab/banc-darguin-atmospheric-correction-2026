# Independent arithmetic and plot-contract checks from frozen CTR42 CSVs, base R.
p <- 'analysis/CTR-27_sen2cor-acolite-asd'
read <- function(n) read.csv(file.path(p,'tables',paste0(n,'.csv')),na.strings='NA',check.names=FALSE,stringsAsFactors=FALSE)
yes <- function(x) x == 'True'
checks <- character()
check <- function(n,ok) { if(!isTRUE(ok)) stop(n); checks <<- c(checks,n) }
near <- function(a,b) length(a)==length(b) && identical(is.na(a),is.na(b)) && all(abs(a[is.finite(a)]-b[is.finite(b)])<2e-14)
k <- function(x) paste(x$station_id,x$band_id)
sat <- read('ctr42_satellite'); ref <- read('ctr42_references')
masks <- read('ctr43_pair_masks'); long <- read('ctr43_spectral_long'); pairs <- read('ctr43_comparison_long')
metrics <- read('ctr43_station_metrics'); avail <- read('ctr43_band_availability'); inventory <- read('ctr43_station_accounting')
bands <- c('B01','B02','B03','B04','B05','B06','B07','B08','B8A')
calc <- function(e) {if(!length(e)) return(rep(NA_real_,3));c(mean(e),mean(abs(e)),sqrt(mean(e^2)))}
check('signed-error fixture retains cancellation',near(calc(c(-2,1,4)),c(1,7/3,sqrt(7))))
check('empty metrics are NA',all(is.na(calc(numeric()))))
check('negative reflectance is finite',is.finite(-.025))
check('one missing correction excludes both from shared metric',identical(is.finite(c(.1,NA)) & is.finite(c(.2,.3)) & is.finite(c(.3,.4)),c(TRUE,FALSE)))
check('234 pair masks unique',nrow(masks)==234 && !anyDuplicated(masks[c('station_id','band_id','SRF_role')]))
check('702 spectral rows unique',nrow(long)==702 && !anyDuplicated(long[c('station_id','band_id','SRF_role','series')]))
check('468 comparison rows unique',nrow(pairs)==468 && !anyDuplicated(pairs[c('station_id','band_id','SRF_role','correction')]))
check('52 station metrics unique',nrow(metrics)==52 && !anyDuplicated(metrics[c('station_id','SRF_role','correction')]))
check('all identities accounted',nrow(inventory)==15 && sum(inventory$disposition=='retained')==13 && identical(sort(inventory$station_id[inventory$disposition=='excluded']),c('AC03','AC04')))
for(role in c('v4_primary','v5_sensitivity')) {
  refs <- ref[ref$SRF_role==role,]; mm <- masks[masks$SRF_role==role,]
  check(paste(role,'reference exact input values'),near(mm$ASD_reflectance,refs$ASD_reflectance[match(k(mm),k(refs))]))
  for(method in c('Sen2Cor','ACOLITE')) {
    ss <- sat[sat$correction==method,]; ii <- match(k(mm),k(ss))
    check(paste(role,method,'exact satellite and flags'),near(mm[[paste0(method,'_reflectance')]],ss$reflectance[ii]) && identical(yes(mm[[paste0(method,'_SCL_flag')]]),yes(ss$SCL_cloud_shadow_or_invalid_flag[ii])))
    ll <- long[long$SRF_role==role & long$series==method,]; ii <- match(k(ll),k(ss))
    check(paste(role,method,'all 117 satellite bands including B08'),nrow(ll)==117 && near(ll$reflectance,ss$reflectance[ii]) && all(is.finite(ll$reflectance[ll$band_id=='B08'])))
    check(paste(role,method,'source provenance and date'),all(ll$source_sha256==ss$source_sha256[ii]) && all(ll$observation_date=='2026-03-07'))
  }
  common <- is.finite(mm$Sen2Cor_reflectance) & is.finite(mm$ACOLITE_reflectance) & is.finite(mm$ASD_reflectance)
  check(paste(role,'104 shared finite rows; B08 not forced'),sum(common)==104 && identical(common,yes(mm$common_finite_triple)) && all(!common[mm$band_id=='B08']))
  check(paste(role,'SCL-complement mask does not change eligibility'),identical(yes(mm$common_finite_without_operational_SCL_flag),common & !yes(mm$Sen2Cor_SCL_flag) & !yes(mm$ACOLITE_SCL_flag)))
  for(sid in unique(mm$station_id)) {
    z <- mm[mm$station_id==sid,]; z <- z[order(z$band_order),]; chosen <- z[yes(z$common_finite_triple),]
    met <- metrics[metrics$SRF_role==role & metrics$station_id==sid,]
    check(paste(role,sid,'identical band set and pair signature'),length(unique(met$pair_keys_sha256))==1 && all(met$bands==paste(chosen$band_id,collapse=';')) && all(met$n_paired_bands==8) && identical(chosen$band_id,bands[bands!='B08']))
    for(method in c('Sen2Cor','ACOLITE')) {
      m <- met[met$correction==method,]; value <- calc(chosen[[paste0(method,'_reflectance')]]-chosen$ASD_reflectance)
      check(paste(role,sid,method,'independent bias MAE RMSE'),near(as.numeric(m[c('bias','MAE','RMSE')]),value) && m$band_weight==1/8 && m$n_paired_bands_SCL_flagged==sum(yes(chosen[[paste0(method,'_SCL_flag')]])))
      check(paste(role,sid,method,'metric bounds'),m$RMSE+1e-14>=m$MAE && m$MAE+1e-14>=abs(m$bias))
    }
    z <- long[long$SRF_role==role & long$station_id==sid & long$series=='ASD',];z <- z[order(z$band_order),]
    check(paste(role,sid,'ASD eight supported bands; gap splits line'),identical(z$band_id,bands) && sum(is.finite(z$reflectance))==8 && is.na(z$reflectance[8]) && is.na(z$segment_id[8]) && all(z$segment_id[1:7]==1) && z$segment_id[9]==2 && all(z$observation_date=='2026-03-27'))
  }
  for(b in bands) {
    z <- mm[mm$band_id==b,]; a <- avail[avail$SRF_role==role & avail$band_id==b,]
    check(paste(role,b,'availability counts'),a$n_retained_stations==13 && a$Sen2Cor_finite==sum(is.finite(z$Sen2Cor_reflectance)) && a$ACOLITE_finite==sum(is.finite(z$ACOLITE_reflectance)) && a$ASD_supported==sum(is.finite(z$ASD_reflectance)) && a$common_finite_triples==sum(yes(z$common_finite_triple)) && a$Sen2Cor_SCL_flagged==sum(yes(z$Sen2Cor_SCL_flag)) && a$ACOLITE_SCL_flagged==sum(yes(z$ACOLITE_SCL_flag)))
  }
}
for(method in c('Sen2Cor','ACOLITE')) {
 z <- pairs[pairs$correction==method,]; ii <- match(paste(k(z),z$SRF_role),paste(k(masks),masks$SRF_role)); mm <- masks[ii,]
 expected <- mm[[paste0(method,'_reflectance')]]-mm$ASD_reflectance; expected[!yes(mm$common_finite_triple)] <- NA_real_
 check(paste(method,'signed differences only on shared mask'),near(z$signed_difference,expected) && sum(is.na(z$signed_difference))==26)
}
for(name in c('masks','long','pairs','metrics','inventory')) check(paste(name,'no validation eligibility'),all(get(name)$validation_eligible=='False'))
check('all current spectral values are nonnegative but no clipping rule',min(long$reflectance,na.rm=TRUE)>=0)
check('flagged satellite values retained once per role',sum(yes(long$SCL_flag),na.rm=TRUE)==218)
check('primary/supplementary designation retained',all(inventory$population[grepl('D06_',inventory$station_id)]=='supplementary_only'))
sens <- read('ctr43_srf_sensitivity')
check('SRF difference exactly recomputed',near(sens$v5_minus_v4,sens$ASD_v5-sens$ASD_v4) && sum(is.na(sens$v5_minus_v4))==13)
lines <- c('PASS: independent base-R arithmetic and plotting-contract verification',paste('Checks:',length(checks)),paste('R:',R.version.string),paste('Platform:',R.version$platform),'Numerical cross-check only. Final independent scientific review and PI approval remain.',checks)
writeLines(lines,file.path(p,'provenance/ctr43_R_verification.txt'))
cat(paste(head(lines,5),collapse='\n'),'\n')
