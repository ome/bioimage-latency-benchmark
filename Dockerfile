FROM rikorose/gcc-cmake
RUN apt-get update && apt-get install -y clang clang-format clang-tidy lldb    
COPY imarisWriter-Setup.sh /tmp
# RUN /tmp/imarisWriter-Setup.sh
CMD ["/bin/bash"]
