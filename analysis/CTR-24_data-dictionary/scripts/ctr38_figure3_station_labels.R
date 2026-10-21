# CTR-38: display-only graphics from frozen CTR-37 tables; no new statistics.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2)
a <- normalizePath(args[1]); out <- args[2]
dir.create(out, recursive=TRUE, showWarnings=FALSE)
read <- function(n) read.csv(file.path(a,'tables',n), na.strings='NA', stringsAsFactors=FALSE)
d <- read('ctr37_spectral_long.csv'); pairs <- read('ctr37_figure_pairs.csv')
m <- read('ctr37_station_metrics.csv')
stations <- c('AC01','AC02','AC05','AC06','AC07','AC08'); bands <- c('B02','B03','B04')
d <- d[d$station_id %in% stations & d$common_finite_triple=='True' & d$SRF_role=='v4_primary',]
pairs <- pairs[pairs$station_id %in% stations & pairs$common_finite_triple=='True' & pairs$station_completeness=='complete' & pairs$SRF_role=='v4_primary',]
stopifnot(nrow(d)==54, nrow(pairs)==36, nrow(m)==12, all(is.finite(d$reflectance)), all(d$included_validation_pair=='False'))
series <- c('ASD','L2A','ACOLITE'); cols <- c('#262626','#D55E00','#0072B2'); symbols <- c(16,17,15); types <- c(1,2,3)
labels <- c('ASD reference (v4)','Sen2Cor L2A','ACOLITE DSF')
# Display names follow the PI request; original classes remain in saved source tables.
display_class <- c(dry_sand="Sand",white_sand="Sand",algae_mud="Macroalgae",seagrass="Seagrass")
classes <- c('dry_sand','algae_mud','white_sand','seagrass'); shapes <- c(21,22,23,24)
bandcols <- c('#0072B2','#009E73','#CC79A7')
lo <- min(0, floor(min(d$reflectance)/0.1)*0.1)
hi <- ceiling(max(d$reflectance)/0.1)*0.1; lim <- c(lo,hi); ticks <- seq(lo,hi,by=.1)
textcol <- '#262626'; gridcol <- '#E4E7E9'
canvas <- function() par(mar=rep(0,4),oma=rep(0,4),family='sans',fg=textcol,col=textcol,cex=1,lend=1)
region <- function(fig, mar=rep(0,4)) {par(fig=fig,mar=mar,new=TRUE);plot.new();plot.window(c(0,1),c(0,1),xaxs='i',yaxs='i')}
station_plot <- function() {
 canvas(); par(new=FALSE);plot.new();plot.window(c(0,1),c(0,1))
 region(c(0,1,.90,1)); text(.04,.73,'Station reflectance across three visible bands',adj=0,cex=1.35,font=2)
 text(.04,.43,'Banc d’Arguin  |  27 March 2026  |  exploratory diagnostics',adj=0,cex=1.0,col='#555555')
 legend(.04,.25,legend=labels,col=cols,pch=symbols,lty=types,lwd=1.4,horiz=TRUE,bty='n',xjust=0,yjust=1,cex=.98,x.intersp=.8,seg.len=1.8)
 for (i in seq_along(stations)) {
  id <- stations[i]; col <- (i-1)%%2; row <- (i-1)%/%2
  x0 <- .09+col*.48; x1 <- x0+.395; top <- .875-row*.27; bottom <- top-.155
  par(fig=c(x0,x1,bottom,top),mar=rep(0,4),new=TRUE)
  plot(NA,xlim=c(.8,3.2),ylim=lim,xaxs='i',yaxs='i',axes=FALSE,xlab='',ylab='')
  abline(h=ticks,col=gridcol,lwd=.65); abline(h=0,col='#9A9A9A',lwd=.7)
  axis(1,at=1:3,labels=bands,tck=-.025,lwd=0,lwd.ticks=.65,col.ticks='#777777',cex.axis=.95,mgp=c(0,.45,0))
  axis(2,at=ticks,labels=formatC(ticks,format='f',digits=1),las=1,tck=-.02,lwd=0,lwd.ticks=.65,col.ticks='#777777',cex.axis=.95,mgp=c(0,.45,0))
  mtext(paste0(LETTERS[i],'  ',id,'  ·  ',display_class[d$class_literal[match(id,d$station_id)]]),side=3,line=.7,adj=0,font=2,cex=1.04)
  for (j in seq_along(series)) {z<-d[d$station_id==id & d$series==series[j],];z<-z[match(bands,z$band_id),];lines(1:3,z$reflectance,col=cols[j],lty=types[j],lwd=1.4);points(1:3,z$reflectance,pch=symbols[j],col=cols[j],cex=.83)}
  # Adjacent metrics are taken directly from the saved table, never recalculated.
  region(c(x0,x1,bottom-.077,bottom-.030))
  xs<-c(0,.36,.65,.93)
  text(xs[1],.85,'N = 3 bands',adj=0,cex=.98,col='#555555',xpd=NA)
  text(xs[-1],.85,c('Bias','MAE','RMSE'),adj=.5,cex=.98,col='#555555',xpd=NA)
  for(j in 1:2) {z<-m[m$station_id==id & m$correction==c('L2A','ACOLITE')[j],];text(xs[1],.85-j*.35,c('Sen2Cor','ACOLITE')[j],adj=0,cex=.98,col=cols[j+1],xpd=NA);text(xs[-1],.85-j*.35,sprintf('%.6f',as.numeric(z[1,c('bias','MAE','RMSE')])),cex=.98,adj=.5,xpd=NA)}
 }
 region(c(0,1,0,.074));text(.5,.75,'Satellite minus ASD defines bias; all values are dimensionless.',cex=.96)
 text(.5,.42,'18 station–band triples on physical hold  ·  0 validation-eligible pairs',cex=.96,font=2)
 text(.5,.10,'Lines show band order only; uncertainty is not estimated.',cex=.93,col='#555555')
 # Common y label is in device coordinates and does not cover axis text.
 region(c(0,.025,.14,.87));text(.5,.5,'Reflectance (1)',srt=90,cex=1.02)
}
export <- function(name, draw, width, height) {
 for(ext in c('png','pdf','svg')) {
  path<-file.path(out,paste0(name,'.',ext))
  if(ext=='png') png(path,width=width,height=height,units='mm',res=600,type='cairo',pointsize=8,bg='white')
  if(ext=='pdf') cairo_pdf(path,width=width/25.4,height=height/25.4,pointsize=8,family='sans',bg='white',onefile=FALSE)
  if(ext=='svg') svg(path,width=width/25.4,height=height/25.4,pointsize=8,family='sans',bg='white',onefile=FALSE)
  draw();dev.off()
 }
}
export('ctr38_figure3_station_spectra',station_plot,180,220)
cat('Display-only station class update; saved numerical values and annotations retained.\n')
