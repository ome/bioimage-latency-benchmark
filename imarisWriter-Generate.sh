#generate files
cd ImarisWriterTest/application
mkdir ImarisFiles
for (( x=256; x<=16384; x=x*2))
do
  for (( z=1; z<=1024; z++))
  do
    for (( t=1; t<=1024; t++))
    do
      for (( c=1; c<=3; c++))
      do
        for (( xc=32; xc<=1024; xc=xc*2))
        do
          for (( zc=1; zc<=32; zc=zc*2))
          do
            ./ImarisWriterTestRelease -sizex $x -sizey $x -sizez $z -sizet $t -sizec $c -chunkx $xc -chunky $xc -chunkz $zc -type 16bit -threads 1 -outputpath ImarisFiles  IMS_XY-$x-Z-$z-T-$t-C-$c-XYC-$xc-ZC-$zc.ims
          done
        done
      done
    done
  done
done

