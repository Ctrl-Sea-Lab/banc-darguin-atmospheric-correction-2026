args <- commandArgs(TRUE); a <- args[1]; lims <- as.numeric(args[2:3]); outputs <- args[4:5]
w <- 3763; h <- 1974; bands <- c('B2','B3','B4','B8'); stats <- c('median','sd')
cols <- list(colorRampPalette(c('#2166AC','#F7F7F7','#B2182B'))(255),hcl.colors(255,'Viridis'))
ix <- seq(1,w,by=3); iy <- seq(1,h,by=3)
maps <- lapply(stats,function(stat) lapply(bands,function(b) {
 f <- file(file.path(a,'outputs',paste0(b,'_',stat,'_display.bin')),'rb'); on.exit(close(f)); m <- matrix(readBin(f,'numeric',n=w*h,size=4,endian='little'),nrow=h,byrow=TRUE); m[iy,ix,drop=FALSE]
}))
render <- function() {
 layout(matrix(seq_len(10),nrow=2,byrow=TRUE),widths=c(1,1,1,1,.32),heights=c(1,1))
 par(oma=c(.4,1,0,0),family='sans',fg='#30343B',col.axis='#30343B',cex=.95)
 for (s in 1:2) {
  for (b in 1:4) {
   par(mar=c(.7,.5,1.7,.5),xaxs='i',yaxs='i')
   z<-maps[[s]][[b]]; z[z < (if(s==1) -lims[s] else 0)] <- (if(s==1) -lims[s] else 0); z[z > lims[s]] <- lims[s]
   image((334050+(ix-.5)*10)/1000,(2209980-(rev(iy)-.5)*10)/1000,t(z[nrow(z):1,,drop=FALSE]),col=cols[[s]],zlim=c(if(s==1) -lims[s] else 0,lims[s]),useRaster=TRUE,asp=1,axes=FALSE,xlab='',ylab='',xlim=c(334.05,371.68),ylim=c(2190.24,2209.98))
   rect(334.05,2190.24,371.68,2209.98,border='#B9BFC5',lwd=.5)
   if(s==1) title(bands[b],line=.4,cex.main=1.15,font.main=2)
   if(b==1) {
    mtext(if(s==1) 'Median' else 'SD',side=2,line=.3,cex=1)
    if(s==2) { segments(336,2191.6,346,2191.6,lwd=2);segments(c(336,346),2191.4,c(336,346),2191.8,lwd=1);text(341,2192.5,'10 km',cex=.75) }
   }
  }
  par(mar=c(1.6,1.2,2,2.5))
  low<-if(s==1) -lims[s] else 0; high<-lims[s]; v<-seq(low,high,length.out=256)
  image(c(0,1),v,matrix(rep(v,each=2),nrow=2),col=cols[[s]],axes=FALSE,xlab='',ylab='',useRaster=TRUE)
  ticks<-if(s==1) c(-1,-.5,0,.5,1)*high else c(0,.5,1)*high
  axis(4,at=ticks,labels=formatC(ticks,format='f',digits=3),las=1,cex.axis=.72,tck=-.15,col='#B9BFC5')
  title(if(s==1) expression(Delta*R) else expression(s[Delta*R]),line=.65,cex.main=.9)
  mtext('(1)',side=1,line=.25,cex=.8)
 }
}
png(outputs[1],width=14,height=4.4,units='in',res=if(length(args)>5) as.numeric(args[6]) else 400,type='cairo');render();dev.off()
if(outputs[2]!='none') {cairo_pdf(outputs[2],width=14,height=4.4);render();dev.off()}
