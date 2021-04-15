FROM continuumio/miniconda3
RUN conda install -c ome bioformats2raw raw2ometiff

#
# Temporary
#
RUN conda install -y -c anaconda -c conda-forge maven git
RUN git clone -b nested-re-re --depth=1 https://github.com/joshmoore/bioformats2raw /tmp/bioformats2raw
RUN git clone -b nested --depth=1 https://github.com/joshmoore/raw2ometiff /tmp/raw2ometiff
RUN git clone -b nested --depth=1 https://github.com/joshmoore/jzarr /tmp/jzarr
RUN cd /tmp/jzarr \
 && echo "bloscJnaLibraryPath=/opt/conda/lib" > maven.properties \
 && mvn install -DskipTests
RUN cd /tmp/bioformats2raw && ./gradlew installDist -x test
RUN cd /tmp/raw2ometiff && ./gradlew installDist -x test
