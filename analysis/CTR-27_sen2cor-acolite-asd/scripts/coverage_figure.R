# CTR-28: supplied S2B response coverage, ASD nm confirmed by PI.
# Run from repository root through scripts/project-env.sh Rscript.
a <- 'analysis/CTR-27_sen2cor-acolite-asd'
d <- read.csv(file.path(a, 'tables/srf_coverage.csv'))
png(file.path(a, 'figures/srf-coverage.png'), width=1600, height=850, res=180)
par(mar=c(6.5,5,4,1))
x <- barplot(100*d$response_fraction_in_ASD_range_if_nm, names.arg=d$band,
 ylim=c(0,110), col=ifelse(d$coverage_pass_if_nm, '#24667c', '#ad593e'),
 ylab='Response inside 400-900 nm (%)', xlab='Sentinel-2B band', las=1,
 main='Spectral support: PI confirms field wavelengths in nm')
abline(h=99.9, lty=2, col='#333333')
text(x, 100*d$response_fraction_in_ASD_range_if_nm+3, sprintf('%.2f',100*d$response_fraction_in_ASD_range_if_nm), cex=.7)
mtext('Supplied SRF v4; dashed line = proposed 99.9% coverage requirement', side=1, line=5, cex=.8)
dev.off()
