#!/usr/bin/env Rscript
# Adapted presentation of the PI's supplied Figure 3; base R avoids new dependencies.
# The original PI script is retained byte-for-byte in provenance/pi_figure3_20261020/.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2L)
a <- normalizePath(args[1]); out <- normalizePath(args[2])
cols <- c(B1="#4c17e1",B2="#6999fe",B3="#a4d26f",B4="#e47121",
          B5="#b80a0a",B6="#7e0000",B7="#111111",B8="#111111",B8A="#111111")
band_names <- c("B1 Coastal","B2 Blue","B3 Green","B4 Red","B5 Red edge",
                "B6 Red edge","B7 Red edge","B8 NIR","B8A Narrow NIR")
shapes <- c("Dry sand"=21,"Algal mud"=23,"White sand"=24,"Seagrass"=25)
metrics <- read.csv(file.path(a,"tables/ctr38_figure3_summary_metrics.csv"))
draw <- function(population) {
  d <- read.csv(file.path(a,paste0("tables/ctr38_figure3_",population,"_pairs.csv")))
  bands <- names(cols)[names(cols) %in% unique(d$band)]
  # Identical scales and a common 1:1 aspect in each panel, including valid negatives.
  lim <- if(population=="reference") c(0,0.7) else c(0,0.6)
  lim <- range(c(lim,d$asd_reflectance,d$satellite_reflectance))
  lim <- c(floor(lim[1]*10)/10,ceiling(lim[2]*10)/10)
  layout(matrix(c(1,2),nrow=1))
  par(family="sans",mar=c(3.5,3.9,2.2,0.6),mgp=c(2.25,0.55,0),tcl=-0.25,
      las=1,cex=0.82,xaxs="i",yaxs="i",lwd=0.8,pty="s")
  for(correction in c("Sen2Cor","ACOLITE")) {
    z <- d[d$correction==correction,]
    m <- metrics[metrics$population==population & metrics$correction==correction,]
    plot(NA,xlim=lim,ylim=lim,asp=1,axes=FALSE,xlab="ASD field reflectance",
         ylab="Satellite surface reflectance")
    axis(1,at=seq(lim[1],lim[2],by=0.1));axis(2,at=seq(lim[1],lim[2],by=0.1));box(bty="l")
    abline(0,1,lty=2,lwd=1,col="#888888")
    points(z$asd_reflectance,z$satellite_reflectance,pch=shapes[z$target],
           bg=cols[z$band],col="#202020",cex=1.20,lwd=0.75)
    title(main=correction,adj=0,line=0.65,cex.main=1.12,xpd=NA)
    text(lim[1]+0.035*diff(lim),lim[2]-0.025*diff(lim),
         sprintf("RMSD %.3f | Bias %+.3f",m$RMSE,m$bias),adj=c(0,1),cex=0.88)
    # Keep each key inside its panel, below and to the right of the plotted values.
    if(correction=="Sen2Cor") {
      legend("bottomright",legend=names(shapes),pch=shapes,pt.bg="white",
             col="#202020",bty="n",cex=0.78,x.intersp=0.65,y.intersp=1.05,
             pt.cex=1.15,inset=c(0.025,0.035))
    } else {
      legend("bottomright",legend=band_names[match(bands,names(cols))],pch=21,
             pt.bg=cols[bands],col="#202020",bty="n",cex=0.74,
             x.intersp=0.65,y.intersp=1.0,pt.cex=1.15,inset=c(0.025,0.035))
    }
  }
}
for(population in c("reference","primary")) {
  name <- file.path(out,paste0("ctr38_figure3_",population))
  svg(paste0(name,".svg"),width=183/25.4,height=100/25.4);draw(population);dev.off()
  cairo_pdf(paste0(name,".pdf"),width=183/25.4,height=100/25.4);draw(population);dev.off()
  png(paste0(name,".png"),width=183,height=100,units="mm",res=600,type="cairo")
  draw(population);dev.off()
}
cat(R.version.string,"\n")
