args <- commandArgs(trailingOnly=TRUE)
p <- args[1]; out <- args[2];dir.create(out,showWarnings=FALSE,recursive=TRUE)
z <- read.csv(file.path(p,'tables/ctr34_local_imagery.csv'))
sites <- c('AC01','AC02','AC05','AC06','AC07','AC08')
png(file.path(out,'ctr34-local-imagery.png'),width=1800,height=1320,res=150)
par(mfrow=c(3,4),mar=c(2,2,2,0.5),oma=c(1,1,2,1))
for(s in sites) for(m in c('L2A','ACOLITE')) {
 d <- z[z$station_id==s & z$method==m,]; rgbz <- array(0,dim=c(11,11,3))
 for(i in 1:3) { v <- d[d$band==c('B04','B03','B02')[i],]; rgbz[,,i] <- matrix(sqrt(pmax(0,pmin(1,v$reflectance/0.6))),nrow=11,byrow=TRUE) }
 plot(c(-55,55),c(-55,55),type='n',asp=1,xlab='',ylab='',axes=FALSE,main=paste(s,m),cex.main=0.9)
 rasterImage(as.raster(rgbz),-55,-55,55,55,interpolate=FALSE)
 rect(-5,-5,5,5,border='white',lwd=1.5);rect(-15,-15,15,15,border='#ffcf40',lty=2)
 points(0,0,pch=3,col='white',cex=.8);axis(1,at=c(-50,0,50),cex.axis=.7);axis(2,at=c(-50,0,50),cex.axis=.7);box()
}
mtext('Native source RGB windows | offsets from containing-cell centre (m) | fixed 0–0.6 stretch, square-root display',outer=TRUE,line=.4,cex=.9)
dev.off()
q <- read.csv(file.path(p,'tables/ctr34_local_qa.csv'));cols <- c('0'='black','1'='red','2'='#555555','3'='#8a5f3d','4'='#398448','5'='#d7bd83','6'='#487da1','7'='gray','8'='white','9'='white','10'='white','11'='cyan')
png(file.path(out,'ctr34-scl.png'),width=1500,height=550,res=150)
par(mfrow=c(1,6),mar=c(2,1,3,1),oma=c(1,1,2,1))
for(s in sites) {
 d <- q[q$station_id==s & q$kind=='SCL',];m <- matrix(cols[as.character(d$raw)],5,5,byrow=TRUE)
 plot(c(-50,50),c(-50,50),type='n',asp=1,axes=FALSE,xlab='',ylab='',main=s,cex.main=.8);rasterImage(as.raster(m),-50,-50,50,50,interpolate=FALSE);rect(-10,-10,10,10,border='white',lwd=2);axis(1,at=c(-40,0,40),cex.axis=.6);box()
}
mtext('SCL native 20 m cells: green = vegetation (4); tan = bare (5); blue = water (6). Centre QA cell outlined.',outer=TRUE,line=.5,cex=.8)
dev.off()
a <- read.csv(file.path(p,'tables/ctr34_current_spectra.csv'))
png(file.path(out,'ctr34-current-spectra.png'),width=1650,height=700,res=150)
par(mfrow=c(1,2),mar=c(4,4,3,1))
for(role in c('primary_intended_held','supplementary_not_primary')) {
 d <- a[a$role==role,]; ss <- unique(d$station_id); cc <- grDevices::hcl.colors(length(ss),'Dark 3')
 plot(c(400,900),c(0,.6),type='n',xlab='Wavelength (nm)',ylab='Reflectance (unitless)',main=if(role=='primary_intended_held') 'Six intended primary targets — matchups held' else 'Seven supplementary targets — outside primary',cex.main=.9)
 for(i in seq_along(ss)) { z <- d[d$station_id==ss[i],];lines(z$wavelength_nm,z$reflectance,col=cc[i],lwd=1.6) }
 legend('topleft',legend=ss,col=cc,lty=1,lwd=2,bty='n',cex=.8)
}
dev.off()
