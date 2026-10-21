#!/usr/bin/env Rscript
# Presentation only: exact independently verified target values; base R/grDevices.
args <- commandArgs(trailingOnly=TRUE); stopifnot(length(args) %in% c(2L,3L))
a <- normalizePath(args[1]); out <- normalizePath(args[2])
d <- read.csv(file.path(a,'tables/ctr48_plot_values.csv'),na.strings=c('NA',''))
ranges <- read.csv(file.path(a,'tables/ctr48_scale_ranges.csv'))
stopifnot(nrow(d)==108L, all(is.finite(d$reflectance)))
ids <- paste0('T',1:6); bands <- c('B01','B02','B03','B04','B05','B06','B07','B08','B8A')
series <- c('Sen2Cor','ACOLITE'); cols <- c(Sen2Cor='#0072B2',ACOLITE='#D55E00')
shapes <- c(Sen2Cor=16,ACOLITE=17); styles <- c(Sen2Cor=1,ACOLITE=2)
x <- d$wavelength_nm[match(bands,d$band_id)]
# NA values are passed through to lines(), which breaks the curve at missing bands.
draw <- function(mode) {
  par(family='sans',mfrow=c(3,2),oma=c(4.4,3.0,5.0,0.4),
      mar=c(3.2,2.7,3.0,0.8),mgp=c(1.8,0.45,0),tcl=-0.23,las=1,
      cex=0.95,xaxs='i',yaxs='i',lwd=0.75)
  axes_record <- list()
  for(i in seq_along(ids)) {
    id <- ids[i]; z <- d[d$target_id==id,]
    lim <- ranges[ranges$target_id==if(mode=='common') 'ALL' else id,]
    yl <- c(lim$suggested_ymin,lim$suggested_ymax)
    stopifnot(all(z$reflectance>=yl[1] & z$reflectance<=yl[2],na.rm=TRUE))
    plot(NA,xlim=c(425,885),ylim=yl,axes=FALSE,xlab='',ylab='')
    ticks <- pretty(yl,n=4); ticks <- ticks[ticks>=yl[1]&ticks<=yl[2]]
    abline(h=ticks,col='#e4e7e9',lwd=0.5)
    if(yl[1]<=0 && yl[2]>=0) abline(h=0,col='#92999e',lty=3,lwd=0.7)
    axis(2,at=ticks,cex.axis=0.90)
    axis(1,at=x,labels=bands,las=2,cex.axis=0.84)
    box(bty='l',col='#666666')
    for(s in series) {
      q <- z[z$correction==s,];q <- q[order(q$band_order_1based),]
      stopifnot(identical(as.character(q$band_id),bands))
      lines(q$wavelength_nm,q$reflectance,col=cols[s],lty=styles[s],lwd=1.2)
      points(q$wavelength_nm,q$reflectance,pch=shapes[s],col=cols[s],cex=0.80)
    }
    title(main=paste0(LETTERS[i],'  ',id,' | ',z$class_literal[1]),adj=0,line=1.25,cex.main=0.91)
    if(id=='T2' && mode=='common') mtext('Thin-cirrus flag; zero cloud probability',side=3,line=0.05,adj=0,cex=0.68,col='#555555')
    axes_record[[i]] <- data.frame(target_id=id,ymin=yl[1],ymax=yl[2])
  }
  mtext('Sen2Cor and ACOLITE | six target spectra',side=3,outer=TRUE,line=3.5,adj=0,cex=1.03,font=2)
  mtext(if(mode=='common') 'Common y scale across all panels' else 'Separate y scales: compare shape within panels; magnitudes across panels differ',
        side=3,outer=TRUE,line=2.15,adj=0,cex=0.76)
  par(fig=c(0,1,0,1),new=TRUE,mar=c(0,0,0,0),oma=c(0,0,0,0))
  plot.new();legend('top',inset=c(0,0.073),horiz=TRUE,bty='n',legend=series,
      col=cols,pch=shapes,lty=styles,lwd=1.2,cex=0.80)
  text(0.018,0.50,'Reflectance (dimensionless)',srt=90,cex=0.83)
  text(0.51,0.043,'Band position follows wavelength; unequal spacing',cex=0.78)
  text(0.51,0.018,'Supplied target classes; lines guide the eye between sampled bands.',cex=0.73,col='#555555')
  do.call(rbind,axes_record)
}
modes <- if(length(args)==3L) args[3] else c('common','custom')
stopifnot(all(modes %in% c('common','custom')))
for(mode in modes) {
  stem <- paste0('ctr49_target_spectra_',mode)
  svg(file.path(out,paste0(stem,'.svg')),width=183/25.4,height=200/25.4,pointsize=9); lim <- draw(mode);dev.off()
  cairo_pdf(file.path(out,paste0(stem,'.pdf')),width=183/25.4,height=200/25.4,pointsize=9);draw(mode);dev.off()
  png(file.path(out,paste0(stem,'.png')),width=183,height=200,units='mm',res=600,type='cairo',pointsize=9);draw(mode);dev.off()
  write.csv(lim,file.path(out,paste0(stem,'_axes.csv')),row.names=FALSE)
  write.csv(d,file.path(out,paste0(stem,'_rows.csv')),row.names=FALSE,na='NA')
}
cat(R.version.string,'\n');print(sessionInfo())
