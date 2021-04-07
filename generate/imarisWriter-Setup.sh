#!/usr/bin/env bash
#hdf5

set -e
set -u
set -x

wget -N -O CMake-hdf5-1.12.0.tar.gz "https://www.hdfgroup.org/package/cmake-hdf5-1-12-0-tar-gz/?wpdmdl=14580&refresh=600867a2422561611163554"
tar -xzf CMake-hdf5-1.12.0.tar.gz
cd CMake-hdf5-1.12.0
./build-unix.sh
cd build
make install
cd ..
cp -r build/_CPack_Packages/Linux/TGZ/HDF5-1.12.0-Linux/HDF_Group/HDF5/1.12.0/share/cmake/szip HDF_Group/HDF5/1.12.0/share/cmake
cp -r build/_CPack_Packages/Linux/TGZ/HDF5-1.12.0-Linux/HDF_Group/HDF5/1.12.0/share/cmake/zlib HDF_Group/HDF5/1.12.0/share/cmake
cp -r build/_CPack_Packages/Linux/TGZ/HDF5-1.12.0-Linux/HDF_Group/HDF5/1.12.0/lib HDF_Group/HDF5/1.12.0
cp -r build/_CPack_Packages/Linux/TGZ/HDF5-1.12.0-Linux/HDF_Group/HDF5/1.12.0/bin HDF_Group/HDF5/1.12.0
cp -r build/_CPack_Packages/Linux/TGZ/HDF5-1.12.0-Linux/HDF_Group/HDF5/1.12.0/include HDF_Group/HDF5/1.12.0
cd ..

#zlib
wget -N -O zlib-1.2.11.tar.gz https://www.zlib.net/zlib-1.2.11.tar.gz
tar -xzf zlib-1.2.11.tar.gz
cd zlib-1.2.11/
./configure --prefix=./zlibInstall
make install
cd ..

#lz4
wget -N -O lz4-dev.zip https://github.com/lz4/lz4/archive/dev.zip
unzip lz4-dev.zip
cd lz4-dev
make DESTDIR=../lz4-install install
cd ..


#imarisWriter
BRANCH=2021-04-07
wget -N -O ImarisWriter.zip https://github.com/ome/ImarisWriter/archive/${BRANCH}.zip
unzip ImarisWriter.zip
mv ImarisWriter-${BRANCH} ImarisWriter
cd ImarisWriter
mkdir release
cd release
cmake -DHDF5_ROOT:PATH="../CMake-hdf5-1.12.0/HDF_Group/HDF5/1.12.0" -DZLIB_ROOT:PATH="../zlib-1.2.11/zlibInstall" -DLZ4_ROOT:PATH="../lz4-dev/lz4-install/usr/local" ..
make install
cd ../..


#imarisWriterTest
BRANCH=2021-04-07
wget -N -O ImarisWriterTest.zip https://github.com/dgault/ImarisWriterTest/archive/${BRANCH}.zip
unzip ImarisWriterTest.zip
mv ImarisWriterTest-${BRANCH} ImarisWriterTest
cd ImarisWriterTest/application
clang++ -std=c++11  -I../.. -L../../ImarisWriter/release/lib -o ImarisWriterTestRelease ImarisWriterTest.cxx -lbpImarisWriter96 -lpthread -rpath ../../CMake-hdf5-1.12.0/HDF_Group/HDF5/1.12.0/lib
cd ../..
