# Reproducible base-R displays; write scratch only, Python promotes through figure_io.
a <- 'analysis/CTR-27_sen2cor-acolite-asd'
out <- commandArgs(trailingOnly=TRUE)[1]
st <- read.csv(file.path(a,'tables/station_crosswalk.csv'), check.names=FALSE)
sp <- read.table(file.path('data/raw/ASD/202603_Reflectance_avg.txt'),header=TRUE,check.names=FALSE)
inv <- read.csv(file.path(a,'tables/aoi_input_inventory.csv'))
paths <- inv$path[inv$used=='True']
l2 <- read.csv(paths[grepl('/Sen2Cor/',paths)])
ac <- read.csv(paths[grepl('/ACOLITE/',paths)])
key <- function(x) paste(x$AOI,x$pixel_id,sep=':')
ac <- ac[match(key(l2),key(ac)),];stopifnot(identical(key(l2),key(ac)))
colors <- c('#0072B2','#D55E00','#009E73','#CC79A7','#332288','#8C510A','#444444','#56B4E9')
draw <- function(name,w,h,fun) {
  png(file.path(out,paste0(name,'.png')),width=w,height=h,units='in',res=100,type='cairo');fun();dev.off()
  pdf(file.path(out,paste0(name,'.pdf')),width=w,height=h,useDingbats=FALSE);fun();dev.off()
}
draw('field-spectra',12,5.7,function(){
 par(mfrow=c(1,2),mar=c(4.5,4.5,3.2,1),oma=c(0,0,1.6,0))
 for(role in c('primary_candidate','supplementary_candidate')) {
  s <- st[st$role==role,]; ys <- as.matrix(sp[,s$asd_column_raw]);
  matplot(sp$wl,ys,type='l',lty=seq_len(nrow(s)),col=colors[seq_len(nrow(s))],lwd=1.6,ylim=c(0,.6),xlab='Wavelength (nm)',ylab='Station-average reflectance (dimensionless)',main=if(role=='primary_candidate') 'Primary candidates: AC01-AC08' else 'Supplementary candidates: D06_A-D06_G')
  legend('topleft',legend=s$station_id,col=colors[seq_len(nrow(s))],lty=seq_len(nrow(s)),lwd=1.6,bty='n',cex=.78,ncol=2)
 }
 mtext('27 March 2026 | Supplied station averages; repeat-level uncertainty unavailable',outer=TRUE,cex=.9)
})
join <- read.csv(file.path(a,'tables/aoi_station_join.csv'))
v <- read.csv(file.path(a,'tables/aoi_plot_vertices.csv'))
draw('station-aoi-map',12,6.5,function(){
 par(mfrow=c(1,2),mar=c(4.5,6,3,1),mgp=c(3,1,0),oma=c(1,0,2.5,0))
 for(g in c('Arel','Iwik')) {
  poly <- v[v$AOI==g,]; cells <- l2[l2$AOI==g,]; s <- join[join$nearest_AOI_raw==g,]
  xx <- range(c(poly$x,s$station_x_m))/1000; yy <- range(c(poly$y,s$station_y_m))/1000
  pad <- max(diff(xx),diff(yy))*.13
  plot(NA,xlim=xx+c(-pad,3*pad),ylim=yy+c(-pad,pad),asp=1,xlab='Easting (km; EPSG:32628)',ylab='',main=paste0(g,': ',nrow(s),' field locations'),axes=FALSE)
  axis(1);axis(2,las=1);box();mtext('Northing (km; EPSG:32628)',side=2,line=4.2)
  rect((cells$x-5)/1000,(cells$y-5)/1000,(cells$x+5)/1000,(cells$y+5)/1000,col='#DCEAF1',border=NA)
  polygon(poly$x/1000,poly$y/1000,border='#0072B2',lwd=1.5)
  points(s$station_x_m/1000,s$station_y_m/1000,pch=ifelse(grepl('^AC',s$station_id),17,1),col='#A54400',cex=1.1)
  ord <- order(s$station_y_m); labely <- seq(min(yy),max(yy),length.out=nrow(s)); labelx <- xx[2]+pad*.8
  segments(s$station_x_m[ord]/1000,s$station_y_m[ord]/1000,labelx,labely,col='#777777',lwd=.6)
  text(labelx,labely,s$station_id[ord],pos=4,cex=.72)
  usr <- par('usr'); bar <- if(g=='Iwik') .5 else .2
  bx <- usr[1]+.06*diff(usr[1:2]); by <- usr[3]+.06*diff(usr[3:4]);segments(bx,by,bx+bar,by,lwd=3);text(bx+bar/2,by,paste(bar*1000,'m'),pos=3,cex=.8)
 }
 mtext('Actual 10 m cell footprints (fill) and supplied AOI outlines | North is up; panel scales differ',outer=TRUE,side=3,line=1,cex=.85)
 mtext('All 15 field locations unmatched. AC01/02: GPS near Iwik; workbook location says Arel. No relocation.',outer=TRUE,side=1,cex=.83)
})
bands <- c('B02','B03','B04')
valid <- function(b,ix) is.finite(l2[ix,b]) & is.finite(ac[ix,b]) & !(l2[ix,b] %in% c(-.1,6.4535))
draw('aoi-correction-comparison',11,7.5,function(){
 par(mfrow=c(2,3),mar=c(4.5,4.5,2.5,1),oma=c(0,0,2.2,0))
 lim <- range(c(as.matrix(l2[,bands]),as.matrix(ac[,bands])))+c(-.015,.015)
 for(g in c('Arel','Iwik')) for(b in bands) {
  ix <- which(l2$AOI==g);ix <- ix[valid(b,ix)]
  plot(l2[ix,b],ac[ix,b],pch=16,col=adjustcolor('#0072B2',alpha.f=.26),cex=.48,xlim=lim,ylim=lim,asp=1,xlab='Operational L2A reflectance (1)',ylab='ACOLITE DSF reflectance (1)',main=paste(g,b,'| n =',length(ix)))
  abline(0,1,col='#444444',lty=2)
 }
 mtext('Exploratory supplied-pixel comparison | QA not validated | Dashed: 1:1 | No ASD matchups',outer=TRUE,cex=.9)
})
draw('aoi-paired-differences',11,7.5,function(){
 par(mfrow=c(2,3),mar=c(5,4.5,2.5,1),oma=c(0,0,2.2,0))
 for(g in c('Arel','Iwik')) for(b in bands) {
  ix <- which(l2$AOI==g);ix <- ix[valid(b,ix)];d <- ac[ix,b]-l2[ix,b]
  hist(d,breaks=seq(-.25,.1,by=.01),xlim=c(-.25,.1),ylim=c(0,750),col='#80B7C9',border='white',main='',xlab='ACOLITE minus operational L2A (1)',ylab='Pixel records')
  title(main=paste(g,b,'| n =',length(d)),line=.5,cex.main=.95)
  abline(v=0,lty=2,col='#444444')
 }
 mtext('Descriptive paired differences | Shared bins and axes | Spatially dependent pixels; QA not validated',outer=TRUE,cex=.9)
})

# Cross-language author verification of all saved descriptive statistics.
check_summary <- function(x,r) {
 z <- c(n=length(x),mean=mean(x),SD=sd(x),Q1=unname(quantile(x,.25,type=7)),median=median(x),Q3=unname(quantile(x,.75,type=7)),minimum=min(x),maximum=max(x))
 stopifnot(isTRUE(all.equal(unname(z),as.numeric(r[1,names(z)]),tolerance=1e-12)))
}
f <- read.csv(file.path(a,'tables/field_spectral_summary.csv'),check.names=FALSE)
for(i in seq_len(nrow(f))) check_summary(sp[[f$ASD_column[i]]],f[i,])
d <- read.csv(file.path(a,'tables/aoi_descriptive.csv'))
for(i in seq_len(nrow(d))) {
 ix <- which(l2$AOI==d$AOI[i]);ix <- ix[valid(d$band[i],ix)]
 x <- if(d$method[i]=='operational L2A') l2[ix,d$band[i]] else ac[ix,d$band[i]]
 check_summary(x,d[i,])
}
d <- read.csv(file.path(a,'tables/aoi_paired_differences.csv'))
for(i in seq_len(nrow(d))) {
 ix <- which(l2$AOI==d$AOI[i]);ix <- ix[valid(d$band[i],ix)]
 check_summary(ac[ix,d$band[i]]-l2[ix,d$band[i]],d[i,])
}
cat('R independently recalculated all 33 summary rows (15 field, 12 product, 6 difference); agreement within 1e-12.\n')
