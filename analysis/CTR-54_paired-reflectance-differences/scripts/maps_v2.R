args <- commandArgs(TRUE)
scratch<-args[1]; a<-args[2]; medlim<-as.numeric(args[3]); outputs<-args[4:6]
w<-as.integer(args[7]); h<-as.integer(args[8]); bands<-c('B2','B3','B4','B8')
# 257 colors put each requested endpoint and the midpoint exactly on an anchor.
cols<-list(colorRampPalette(c('#2166AC','#F7F7F7','#B2182B'))(255),colorRampPalette(c('#2166AC','#FFFFFF','#B2182B'))(257))
anchor_values<-c(0,.01,.02); anchor_index<-1+round(anchor_values/.02*256)
actual<-toupper(cols[[2]][anchor_index]); expected<-c('#2166AC','#FFFFFF','#B2182B')
stopifnot(identical(actual,expected))
write.csv(data.frame(sd=anchor_values,index=anchor_index,hex=actual,expected=expected,pass=actual==expected),file.path(a,'tables/color_anchors_v2.csv'),row.names=FALSE)
ix<-unique(round(seq(1,w,length.out=ceiling(w/2)))); iy<-unique(round(seq(1,h,length.out=ceiling(h/2))))
maps<-lapply(c('median','sd'),function(stat) lapply(bands,function(b) {
 f<-file(file.path(scratch,paste0(b,'_',stat,'.bin')),'rb'); on.exit(close(f))
 m<-matrix(readBin(f,'numeric',n=w*h,size=4,endian='little'),nrow=h,byrow=TRUE)
 m[iy,ix,drop=FALSE]
}))
render<-function() {
 par(mar=rep(0,4),oma=rep(0,4),family='sans',xaxs='i',yaxs='i')
 panel_w<-.221; panel_h<-panel_w*20*(1974/3763)/6.1
 bottoms<-c(.943-panel_h,.475-panel_h)
 geometry<-list()
 for(s in 1:2) {
  lo<-if(s==1) -medlim else 0; hi<-if(s==1) medlim else .02
  for(b in 1:4) {
   left<-.029+(b-1)*(.221+.008)
   par(fig=c(left,left+panel_w,bottoms[s],bottoms[s]+panel_h),new=(s!=1||b!=1))
   plot.new(); plot.window(xlim=c(334.05,371.68),ylim=c(2190.24,2209.98),asp=1)
   z<-maps[[s]][[b]]
   index<-1+floor(pmax(0,pmin(1,(z-lo)/(hi-lo)))*(length(cols[[s]])-1)+.5)
   color<-matrix(cols[[s]][index],nrow=nrow(z)); color[!is.finite(z)]<-'#D9D9D9'
   rasterImage(as.raster(color),334.05,2190.24,371.68,2209.98,interpolate=FALSE)
   rect(334.05,2190.24,371.68,2209.98,border='#A7ADB3',lwd=.5)
   geometry[[length(geometry)+1]]<-data.frame(statistic=c('median','sd')[s],band=bands[b],width_inches=par('pin')[1],height_inches=par('pin')[2],xmin=334050,xmax=371680,ymin=2190240,ymax=2209980)
   if(s==2 && b==1) {segments(336,2191.6,346,2191.6,lwd=2); segments(c(336,346),2191.4,c(336,346),2191.8,lwd=1); text(341,2192.7,'10 km',cex=.7)}
  }
  # Compact shared vertical legend; triangles disclose display saturation.
  par(fig=c(.947,.960,bottoms[s]+.018,bottoms[s]+panel_h-.018),new=TRUE)
  plot.new(); plot.window(xlim=c(0,1),ylim=c(lo,hi))
  zz<-seq(lo,hi,length.out=length(cols[[s]])+1)
  rect(0,head(zz,-1),1,tail(zz,-1),col=cols[[s]],border=NA)
  ticks<-if(s==1) c(-medlim,0,medlim) else c(0,.01,.02)
  axis(4,at=ticks,labels=if(s==1) formatC(ticks,digits=3,format='f') else c('0','0.01','0.02'),las=1,cex.axis=.72,tck=-.12,col='#666666',mgp=c(0,.35,0))
  par(xpd=NA)
  if(s==2) polygon(c(0,.5,1),c(hi,hi+.045*(hi-lo),hi),col=tail(cols[[s]],1),border=NA)
  if(s==1) polygon(c(0,.5,1),c(lo,lo-.045*(hi-lo),lo),col=cols[[s]][1],border=NA)
 }
 par(fig=c(0,1,0,1),new=TRUE,mar=rep(0,4));plot.new();plot.window(c(0,1),c(0,1))
 for(b in 1:4) text(.029+(b-1)*(.221+.008)+.221/2,.978,bands[b],font=2,cex=1.05)
 text(.012,bottoms[1]+panel_h/2,'Median',srt=90,cex=.9)
 text(.012,bottoms[2]+panel_h/2,'SD',srt=90,cex=.9)
 text(.951,.971,expression(Delta*R),cex=.85)
 text(.951,.505,expression(s[Delta*R]),cex=.85)
 text(.951,.045,'(1)',cex=.72)
 write.csv(do.call(rbind,geometry),file.path(a,'tables/panel_geometry_v2.csv'),row.names=FALSE)
}
png(outputs[1],width=20,height=6.1,units='in',res=400,pointsize=16,type='cairo');render();dev.off()
cairo_pdf(outputs[2],width=20,height=6.1,pointsize=16);render();dev.off()
png(outputs[3],width=20,height=6.1,units='in',res=120,pointsize=16,type='cairo');render();dev.off()
