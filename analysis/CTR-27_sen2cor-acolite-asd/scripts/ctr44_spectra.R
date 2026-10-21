#!/usr/bin/env Rscript
# Presentation only: consume the verified CTR43 rows without numerical processing.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2L)
a <- normalizePath(args[1]); out <- normalizePath(args[2])
d <- read.csv(file.path(a,'tables/ctr43_spectral_long.csv'),na.strings='NA')
d <- d[d$SRF_role=='v4_primary',]
write.csv(d,file.path(out,'ctr44_plot_rows.csv'),row.names=FALSE,na='NA')
account <- read.csv(file.path(a,'tables/ctr43_station_accounting.csv'))
classes <- c(dry_sand='Sand',white_sand='Sand',algae_mud='Macroalgae',seagrass='Seagrass',sand='Sand',zn='zn (original label)')
series <- c('ASD','Sen2Cor','ACOLITE')
cols <- c(ASD='#222222',Sen2Cor='#0072B2',ACOLITE='#D55E00')
pch <- c(ASD=15,Sen2Cor=16,ACOLITE=17)
lty <- c(ASD=3,Sen2Cor=1,ACOLITE=2)
bands <- c('B01','B02','B03','B04','B05','B06','B07','B08','B8A')
x <- d$plot_wavelength_nm[match(bands,d$band_id)]
ylim <- range(c(0,d$reflectance),na.rm=TRUE)
ylim <- c(floor(ylim[1]*5)/5,ceiling(ylim[2]*5)/5)
# One scale across both plates; finite negatives are retained automatically.
draw <- function(pop) {
  ids <- account$station_id[account$population==pop]
  nr <- ceiling(length(ids)/2)
  par(family='sans',mfrow=c(nr,2),oma=c(4.3,3.1,7.2,0.5),
      mar=c(3.2,2.7,2.9,0.8),mgp=c(1.8,0.45,0),tcl=-0.23,las=1,
      cex=0.82,xaxs='i',yaxs='i',lwd=0.75)
  for(i in seq_along(ids)) {
    id <- ids[i]; z <- d[d$station_id==id,]
    plot(NA,xlim=c(425,885),ylim=ylim,axes=FALSE,xlab='',ylab='')
    abline(h=pretty(ylim,n=4),col='#e4e7e9',lwd=0.5)
    axis(2,at=pretty(ylim,n=4),cex.axis=0.82)
    axis(1,at=x,labels=bands,las=2,cex.axis=0.70)
    box(bty='l',col='#666666')
    for(s in series) {
      q <- z[z$series==s,];q <- q[order(q$band_order),]
      for(seg in unique(q$segment_id[!is.na(q$segment_id)])) {
        v <- q[!is.na(q$segment_id)&q$segment_id==seg,]
        lines(v$plot_wavelength_nm,v$reflectance,col=cols[s],lty=lty[s],lwd=1.1)
      }
      points(q$plot_wavelength_nm,q$reflectance,pch=pch[s],col=cols[s],cex=0.78)
      flagged <- !is.na(q$SCL_flag) & q$SCL_flag=='True'
      points(q$plot_wavelength_nm[flagged],q$reflectance[flagged],pch=1,col='#111111',cex=1.25,lwd=0.7)
    }
    title(main=paste0(LETTERS[i],'  ',id,' | ',classes[z$class_literal[1]]),adj=0,line=1.5,cex.main=0.95)
    mtext('ASD B08: NA [COV]',side=3,line=0.25,adj=0,cex=0.73,col='#555555')
  }
  if(length(ids)%%2==1) {plot.new();text(0,0.75,'Supplementary identities retained',adj=0,cex=0.93,font=2);text(0,0.60,'zn is an original label; no new class assigned.\nAll nine satellite bands are shown.\nNo validation-eligible pairs.',adj=c(0,1),cex=0.85)}
  mtext(if(pop=='primary_intended') '7 March satellite spectra | six primary stations' else '7 March satellite spectra | seven supplementary stations',side=3,outer=TRUE,line=5.6,adj=0,cex=1.0,font=2)
  mtext('Sen2Cor / ACOLITE: 7 Mar 2026   |   ASD: 27 Mar 2026 (20 days later)',side=3,outer=TRUE,line=4.2,adj=0,cex=0.82)
  par(fig=c(0,1,0,1),new=TRUE,mar=c(0,0,0,0),oma=c(0,0,0,0))
  plot.new();legend('top',inset=c(0,if(pop=='primary_intended') 0.075 else 0.060),horiz=TRUE,bty='n',
       legend=c('ASD (v4 bands)','Sen2Cor','ACOLITE','SCL cloud / shadow'),
       col=c(cols,'#111111'),pch=c(pch,1),lty=c(lty,NA),lwd=1.1,cex=0.75,pt.cex=c(0.8,0.8,0.8,1.2))
  text(0.018,0.50,'Reflectance (1)',srt=90,cex=0.83)
  text(0.51,0.045,'Band at common display wavelength (nm); unequal band spacing',cex=0.78)
  text(0.51,0.018,'COV = insufficient ASD response coverage; lines guide the eye within available segments.',cex=0.72,col='#555555')
}
for(pop in c('primary_intended','supplementary_only')) {
  stem <- if(pop=='primary_intended') 'ctr44_march_primary' else 'ctr44_march_supplementary'
  h <- if(pop=='primary_intended') 200 else 250
  svg(file.path(out,paste0(stem,'.svg')),width=183/25.4,height=h/25.4,pointsize=9);draw(pop);dev.off()
  cairo_pdf(file.path(out,paste0(stem,'.pdf')),width=183/25.4,height=h/25.4,pointsize=9);draw(pop);dev.off()
  png(file.path(out,paste0(stem,'.png')),width=183,height=h,units='mm',res=600,type='cairo',pointsize=9);draw(pop);dev.off()
}
cat(R.version.string,'\n')
