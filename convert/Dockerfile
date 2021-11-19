FROM continuumio/miniconda3:4.9.2
RUN conda install -c ome bioformats2raw raw2ometiff

#
# Temporary
#
RUN conda install -y -c anaconda -c conda-forge maven git
RUN conda update -c conda-forge openjdk # Upgrade from JDK8 to JDK11 to fix mvn issues
RUN git clone -b 2021-04-17 --depth=1 https://github.com/ome/bioformats2raw /tmp/bioformats2raw
RUN git clone -b 2021-04-17 --depth=1 https://github.com/ome/raw2ometiff /tmp/raw2ometiff
RUN git clone -b 2021-04-17 --depth=1 https://github.com/ome/jzarr /tmp/jzarr
RUN cd /tmp/jzarr \
 && echo "bloscJnaLibraryPath=/opt/conda/lib" > maven.properties \
 && mvn install -DskipTests
RUN cd /tmp/bioformats2raw && ./gradlew installDist -x test
RUN cd /tmp/raw2ometiff && ./gradlew installDist -x test
