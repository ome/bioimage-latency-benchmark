FROM rikorose/gcc-cmake
RUN apt-get update && apt-get install -y clang clang-format clang-tidy lldb
COPY imarisWriter-Setup.sh /tmp
RUN /tmp/imarisWriter-Setup.sh
ENV LD_LIBRARY_PATH=/ImarisWriter/release/lib:/CMake-hdf5-1.12.0/HDF_Group/HDF5/1.12.0/lib/
COPY imarisWriter-Generate.sh /tmp
ENTRYPOINT ["/tmp/imarisWriter-Generate.sh"]
