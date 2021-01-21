/***************************************************************************
 *   Copyright (c) 2020-present Bitplane AG Zuerich                        *
 *                                                                         *
 *   Licensed under the Apache License, Version 2.0 (the "License");       *
 *   you may not use this file except in compliance with the License.      *
 *   You may obtain a copy of the License at                               *
 *                                                                         *
 *       http://www.apache.org/licenses/LICENSE-2.0                        *
 *                                                                         *
 *   Unless required by applicable law or agreed to in writing, software   *
 *   distributed under the License is distributed on an "AS IS" BASIS,     *
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or imp   *
 *   See the License for the specific language governing permissions and   *
 *   limitations under the License.                                        *
 ***************************************************************************/
#include "bpBCommandLine.h"

#define bpCommandLine bpBCommandLine

#include "ImarisWriter/interface/bpImageConverter.h"

#include <random>


#include <sys/time.h>

#if defined(_WIN32)
#include <windows.h>
#elif defined(__APPLE__)
#include <mach/mach.h>
#include <mach/mach_time.h>
#else
#include <time.h>
#endif

#include <fstream>
#include <iostream>
#include <map>
#include <list>

#include <string>
#include <cstdint>
#include <chrono>
#include <algorithm>
#include <random>

void RecordProgress(bpFloat aProgress, bpUInt64 aTotalBytesWritten, int& aOldProgress)
{
  int vProgress = (int)(aProgress * 100);
  if (vProgress - aOldProgress < 5) {
    return;
  }
  if (aTotalBytesWritten < 10 * 1024 * 1024) {
    std::cout << "Progress: " << vProgress << "% [" << (aTotalBytesWritten / 1024) << "KB]" << std::endl;
  }
  else {
    std::cout << "Progress: " << vProgress << "% [" << (aTotalBytesWritten / (1024 * 1024)) << "MB]" << std::endl;
  }
  aOldProgress = vProgress;
}

bpUInt64 PerformanceCounter()
{
#if defined(_WIN32)
  LARGE_INTEGER vTime;
  QueryPerformanceCounter(&vTime);
  return static_cast<bpUInt64>(vTime.QuadPart);
#else
  struct timespec vTimeSpec;
  //clock_gettime(CLOCK_MONOTONIC, &vTimeSpec);
  localtime((const long *)&vTimeSpec);
  //gettimeofday(&vTimeSpec, NULL);
  return vTimeSpec.tv_sec + vTimeSpec.tv_nsec / 1000000000.0;
#endif
}

bpUInt64 PerformanceFrequency()
{
#if defined(_WIN32)
  LARGE_INTEGER vFrequency;
  QueryPerformanceFrequency(&vFrequency);
  return static_cast<bpUInt64>(vFrequency.QuadPart);
#else
  return 1;
#endif
}

int main(int argc, char* argv[])
{

  try {
    bpCommandLine vCommandLine(0, 1);
    vCommandLine.allowArgument("sizex", "Image Size X (default 1024)", 1);
    vCommandLine.allowArgument("sizey", "Image Size Y (default 1024)", 1);
    vCommandLine.allowArgument("sizez", "Image Size Z (default 1)", 1);
    vCommandLine.allowArgument("sizet", "Image Size T (default 1)", 1);
    vCommandLine.allowArgument("sizec", "Image Size C (default 1)", 1);
    vCommandLine.allowArgument("chunkx", "Chunk Size X (default 256)", 1);
    vCommandLine.allowArgument("chunky", "Chunk Size Y (default 256)", 1);
    vCommandLine.allowArgument("chunkz", "Chunk Size Z (default 8)", 1);
    vCommandLine.allowArgument("chunkct", "Chunk Size T (default 1)", 1);
    vCommandLine.allowArgument("chunkc", "Chunk Size C (default 1)", 1);
    vCommandLine.allowArgument("threads", "Number of Threads (default 8)", 1);
    vCommandLine.allowArgument("compression", "Compression type and level (default 2)", 1);
    vCommandLine.allowArgument("logfile", "Log File Path", 1);
    vCommandLine.allowArgument("type", "DataType 8bit or 16bit", 1);
    vCommandLine.allowArgument("outputpath", "Set the output folder", 1);
    vCommandLine.allowArgument("randseed", "Fix seed for random number to reproduce results", 1);
    vCommandLine.allowArgument("z1", "Force block size Z = 1 (optional flag, no argument values)", 0);

    vCommandLine.Parse(argc, argv);

    bpString vFileName = vCommandLine.GetOutFileName();
    if (vFileName.empty()) {
      throw bpArgumentException("No OutFile specified.");
    }

    std::string vOutpath = "";
    if (vCommandLine.Found("outputpath")) {
      vCommandLine.GetValue("outputpath", vOutpath);
    }

    bpString vOutputFilePath = vOutpath + "/" + vFileName;

    bpSize vSizeX(1024);
    if (vCommandLine.Found("sizex")) {
      vCommandLine.GetValue("sizex", vSizeX);
    }
    else {
      std::cerr << "Using default sizex 1024\n";
    }
    bpSize vSizeY(1024);
    if (vCommandLine.Found("sizey")) {
      vCommandLine.GetValue("sizey", vSizeY);
    }
    else {
      std::cerr << "Using default sizey 1024\n";
    }
    bpSize vSizeZ(1);
    if (vCommandLine.Found("sizez")) {
      vCommandLine.GetValue("sizez", vSizeZ);
    }
    else {
      std::cerr << "Using default sizez 1\n";
    }
    bpSize vSizeT(1);
    if (vCommandLine.Found("sizet")) {
      vCommandLine.GetValue("sizet", vSizeT);
    }
    else {
      std::cerr << "Using default sizet 1\n";
    }
    bpSize vSizeC(1);
    if (vCommandLine.Found("sizec")) {
      vCommandLine.GetValue("sizec", vSizeC);
    }
    else {
      std::cerr << "Using default sizec 1\n";
    }

    bpSize vChunkSizeX(256);
    if (vCommandLine.Found("chunkx")) {
      vCommandLine.GetValue("chunkx", vChunkSizeX);
    }
    bpSize vChunkSizeY(256);
    if (vCommandLine.Found("chunky")) {
      vCommandLine.GetValue("chunky", vChunkSizeY);
    }
    bpSize vChunkSizeZ(8);
    if (vCommandLine.Found("chunkz")) {
      vCommandLine.GetValue("chunkz", vChunkSizeZ);
    }
    bpSize vChunkSizeT(1);
    if (vCommandLine.Found("chunkt")) {
      vCommandLine.GetValue("chunkt", vChunkSizeT);
    }
    bpSize vChunkSizeC(1);
    if (vCommandLine.Found("chunkc")) {
      vCommandLine.GetValue("chunkc", vChunkSizeC);
    }

    bpSize vNumberOfThreads(8);
    if (vCommandLine.Found("threads")) {
      vCommandLine.GetValue("threads", vNumberOfThreads);
    }
    else {
      std::cerr << "Using default " << vNumberOfThreads << " threads\n";
    }

    bpSize vCompression(2);
    if (vCommandLine.Found("compression")) {
      vCommandLine.GetValue("compression", vCompression);
    }
    else {
      std::cerr << "Using default compression level " << vCompression << "\n";
    }

    bpString vLogFilePath;
    if (vCommandLine.Found("logfile")) {
      vCommandLine.GetValue("logfile", vLogFilePath);
    }

    bpString vDataType("16bit");
    if (vCommandLine.Found("type")) {
      vCommandLine.GetValue("type", vDataType);
    }
    else {
      std::cerr << "Using default type 16bit\n";
    }

    bool vForceFileBlockSizeZ1 = vCommandLine.Found("z1");

    bpUInt32 vRandSeed(0);
    if (vCommandLine.Found("randseed")) {
      bpSize vValue(0);
      vCommandLine.GetValue("randseed", vValue);
      vRandSeed = (bpUInt32)vValue;
    }
    else {
      std::random_device rd;
      vRandSeed = rd();
      std::cerr << "Using random seed " << vRandSeed << "\n";
    }

    int vProgress = -5;
    bpConverterTypes::tProgressCallback vProgressCallback = [&vProgress](bpFloat aProgress, bpUInt64 aTotalBytesWritten) {
      RecordProgress(aProgress, aTotalBytesWritten, vProgress);
    };

    bpConverterTypes::cOptions vOptions;
    vOptions.mForceFileBlockSizeZ1 = vForceFileBlockSizeZ1;
    vOptions.mNumberOfThreads = vNumberOfThreads;
    vOptions.mCompressionAlgorithmType = bpConverterTypes::eCompressionAlgorithmGzipLevel2;
    bpConverterTypes::tCompressionAlgorithmType vAlgorithmType = (bpConverterTypes::tCompressionAlgorithmType) vCompression;
    switch (vAlgorithmType) {
    case bpConverterTypes::eCompressionAlgorithmGzipLevel1:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel2:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel3:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel4:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel5:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel6:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel7:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel8:
    case bpConverterTypes::eCompressionAlgorithmGzipLevel9:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel1:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel2:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel3:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel4:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel5:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel6:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel7:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel8:
    case bpConverterTypes::eCompressionAlgorithmShuffleGzipLevel9:
    case bpConverterTypes::eCompressionAlgorithmLZ4:
    case bpConverterTypes::eCompressionAlgorithmShuffleLZ4:
      vOptions.mCompressionAlgorithmType = vAlgorithmType;
      break;
    default:
      vOptions.mCompressionAlgorithmType = bpConverterTypes::eCompressionAlgorithmNone;
    }
    bpConverterTypes::tSize5D vImageSize(bpConverterTypes::X, vSizeX, bpConverterTypes::Y, vSizeY, bpConverterTypes::Z, vSizeZ, bpConverterTypes::C, vSizeC, bpConverterTypes::T, vSizeT);

    if (vDataType == bpString("16bit")) {
      std::cout << "Starting writer test " << " using " << vNumberOfThreads << " thread(s)"<< std::endl;

      bpConverterTypes::cImageExtent vImageExtent{ 0,0,0,10,10,10 };
      bpConverterTypes::tDataType vImageDataType = bpConverterTypes::bpUInt16Type;
      bpConverterTypes::tDimensionSequence5D vDimensionSequence(bpConverterTypes::X, bpConverterTypes::Y, bpConverterTypes::Z, bpConverterTypes::C, bpConverterTypes::T);
      //bpConverterTypes::tDimensionSequence5D vDimensionSequence(bpConverterTypes::X, bpConverterTypes::Y, bpConverterTypes::Z, bpConverterTypes::C, bpConverterTypes::T);
      bpConverterTypes::tSize5D vSample(bpConverterTypes::X, 1, bpConverterTypes::Y, 1, bpConverterTypes::Z, 1, bpConverterTypes::C, 1, bpConverterTypes::T, 1);
      //bpConverterTypes::tSize5D vInputBlockSize5D(bpConverterTypes::X, 256, bpConverterTypes::Y, 64, bpConverterTypes::Z, 32, bpConverterTypes::C, 1, bpConverterTypes::T, 1);
      bpConverterTypes::tSize5D vInputBlockSize5D(bpConverterTypes::X, vChunkSizeX, bpConverterTypes::Y, vChunkSizeY, bpConverterTypes::Z, vChunkSizeZ, bpConverterTypes::C, vChunkSizeC, bpConverterTypes::T, vChunkSizeT);
      //bpConverterTypes::tSize5D vInputBlockSize5D(bpConverterTypes::X, 512, bpConverterTypes::Y, 512, bpConverterTypes::Z, 1, bpConverterTypes::C, 1, bpConverterTypes::T, 1);
      bpSize vInputBlockSize = vInputBlockSize5D[bpConverterTypes::X] * vInputBlockSize5D[bpConverterTypes::Y] * vInputBlockSize5D[bpConverterTypes::Z] * vInputBlockSize5D[bpConverterTypes::C] * vInputBlockSize5D[bpConverterTypes::T];
      bpSize vNBlocksX = (vImageSize[bpConverterTypes::X] - 1) / vInputBlockSize5D[bpConverterTypes::X] + 1;
      bpSize vNBlocksY = (vImageSize[bpConverterTypes::Y] - 1) / vInputBlockSize5D[bpConverterTypes::Y] + 1;
      bpSize vNBlocksZ = (vImageSize[bpConverterTypes::Z] - 1) / vInputBlockSize5D[bpConverterTypes::Z] + 1;
      bpSize vNBlocksC = (vImageSize[bpConverterTypes::C] - 1) / vInputBlockSize5D[bpConverterTypes::C] + 1;
      bpSize vNBlocksT = (vImageSize[bpConverterTypes::T] - 1) / vInputBlockSize5D[bpConverterTypes::T] + 1;
      bpSize vImageSizePixels = vImageSize[bpConverterTypes::X] * vImageSize[bpConverterTypes::Y] * vImageSize[bpConverterTypes::Z] * vImageSize[bpConverterTypes::C] * vImageSize[bpConverterTypes::T];
      bpSize vImageSizeInMB = vImageSizePixels * sizeof(bpUInt16) / 1024 / 1024 ;
      bpString vOutputFile = vOutputFilePath;

      bpUInt16* vFileBlock = new bpUInt16[2 * vInputBlockSize];
      std::mt19937 mt(vRandSeed);
      std::normal_distribution<> dist(100.0, 40.0);
      std::uniform_int_distribution<> uniform(0, vInputBlockSize);
      double vPrevious = dist(mt);
      bpFloat vCorrelationCoefficient = 0.7f;
      for (bpSize vVoxelIndex = 0; vVoxelIndex < 2 * vInputBlockSize; ++vVoxelIndex) {
        double vRandom = (1 - vCorrelationCoefficient) * dist(mt) + vCorrelationCoefficient * vPrevious;
        vFileBlock[vVoxelIndex] = vRandom > 0 ? (vRandom < (1 << 12) ? vRandom : (1<<12)) : 0;
      }
      bpUInt64 vFrequency = PerformanceFrequency();
      bpUInt64 vStartTime = 0;
      bpUInt64 vEndTime = vStartTime;
      bpSize vTimeInMilliSeconds = 0;

      {
        std::cout << "Input block size XYZCT: " << vInputBlockSize5D[bpConverterTypes::X] << " " << vInputBlockSize5D[bpConverterTypes::Y] << " " <<
          vInputBlockSize5D[bpConverterTypes::Z] << " " << vInputBlockSize5D[bpConverterTypes::C] << " " << vInputBlockSize5D[bpConverterTypes::T] << std::endl;

        vStartTime = PerformanceCounter();
        bpImageConverter<bpUInt16> vImageConverter(
          vImageDataType, vImageSize, vSample, vDimensionSequence, vInputBlockSize5D,
          vOutputFile, vOptions, "ImarisWriterTest", "1.0", vProgressCallback);
        bpConverterTypes::tIndex5D vBlockIndex(bpConverterTypes::X, 0, bpConverterTypes::Y, 0, bpConverterTypes::Z, 0, bpConverterTypes::C, 0, bpConverterTypes::T, 0);
        for (bpSize vBlockIndexT = 0; vBlockIndexT < vNBlocksT; vBlockIndexT++) {
          vBlockIndex[bpConverterTypes::T] = vBlockIndexT;
          for (bpSize vBlockIndexC = 0; vBlockIndexC < vNBlocksC; vBlockIndexC++) {
            vBlockIndex[bpConverterTypes::C] = vBlockIndexC;
            for (bpSize vBlockIndexZ = 0; vBlockIndexZ < vNBlocksZ; vBlockIndexZ++) {
              vBlockIndex[bpConverterTypes::Z] = vBlockIndexZ;
              for (bpSize vBlockIndexY = 0; vBlockIndexY < vNBlocksY; vBlockIndexY++) {
                vBlockIndex[bpConverterTypes::Y] = vBlockIndexY;
                for (bpSize vBlockIndexX = 0; vBlockIndexX < vNBlocksX; vBlockIndexX++) {
                  vBlockIndex[bpConverterTypes::X] = vBlockIndexX;
                  bpSize vRandomOffset = uniform(mt);
                  vImageConverter.CopyBlock(vFileBlock + vRandomOffset, vBlockIndex);
                }
              }
            }
          }
        }

        bpConverterTypes::tColorInfoVector vColorInfoPerChannel(vImageSize[bpConverterTypes::C]);
        bpConverterTypes::tTimeInfoVector vTimeInfoPerTimePoint;
        bpConverterTypes::tParameters vParameters;
        vParameters["Image"]["ImageSizeInMB"] = vImageSizeInMB;
        vImageConverter.Finish(vImageExtent, vParameters, vTimeInfoPerTimePoint, vColorInfoPerChannel, false);

        vEndTime = PerformanceCounter();
        vTimeInMilliSeconds = (vEndTime - vStartTime) * 1000 / vFrequency;
      }

      std::cout << "Writer: " << "  MB: " << vImageSizeInMB << "     Time[ms]: " << vTimeInMilliSeconds << "\n";

      delete[] vFileBlock;

      //Sleep(500);
    } else
    if (vDataType == bpString("8bit")) {
      std::cout << "Starting writer test " << " using " << vNumberOfThreads << " thread(s)" << std::endl;

      bpConverterTypes::cImageExtent vImageExtent{ 0,0,0,10,10,10 };
      bpConverterTypes::tDataType vImageDataType = bpConverterTypes::bpUInt8Type;
      bpConverterTypes::tDimensionSequence5D vDimensionSequence(bpConverterTypes::X, bpConverterTypes::Y, bpConverterTypes::Z, bpConverterTypes::C, bpConverterTypes::T);
      //bpConverterTypes::tDimensionSequence5D vDimensionSequence(bpConverterTypes::X, bpConverterTypes::Y, bpConverterTypes::Z, bpConverterTypes::C, bpConverterTypes::T);
      bpConverterTypes::tSize5D vSample(bpConverterTypes::X, 1, bpConverterTypes::Y, 1, bpConverterTypes::Z, 1, bpConverterTypes::C, 1, bpConverterTypes::T, 1);
      //bpConverterTypes::tSize5D vInputBlockSize5D(bpConverterTypes::X, 256, bpConverterTypes::Y, 64, bpConverterTypes::Z, 32, bpConverterTypes::C, 1, bpConverterTypes::T, 1);
      bpConverterTypes::tSize5D vInputBlockSize5D(bpConverterTypes::X, vChunkSizeX, bpConverterTypes::Y, vChunkSizeY, bpConverterTypes::Z, vChunkSizeZ, bpConverterTypes::C, vChunkSizeC, bpConverterTypes::T, vChunkSizeT);
      bpSize vInputBlockSize = vInputBlockSize5D[bpConverterTypes::X] * vInputBlockSize5D[bpConverterTypes::Y] * vInputBlockSize5D[bpConverterTypes::Z] * vInputBlockSize5D[bpConverterTypes::C] * vInputBlockSize5D[bpConverterTypes::T];
      bpSize vNBlocksX = (vImageSize[bpConverterTypes::X] - 1) / vInputBlockSize5D[bpConverterTypes::X] + 1;
      bpSize vNBlocksY = (vImageSize[bpConverterTypes::Y] - 1) / vInputBlockSize5D[bpConverterTypes::Y] + 1;
      bpSize vNBlocksZ = (vImageSize[bpConverterTypes::Z] - 1) / vInputBlockSize5D[bpConverterTypes::Z] + 1;
      bpSize vNBlocksC = (vImageSize[bpConverterTypes::C] - 1) / vInputBlockSize5D[bpConverterTypes::C] + 1;
      bpSize vNBlocksT = (vImageSize[bpConverterTypes::T] - 1) / vInputBlockSize5D[bpConverterTypes::T] + 1;
      bpSize vNBlocks = vNBlocksX * vNBlocksY * vNBlocksZ * vNBlocksC * vNBlocksT;
      bpSize vImageSizePixels = vImageSize[bpConverterTypes::X] * vImageSize[bpConverterTypes::Y] * vImageSize[bpConverterTypes::Z] * vImageSize[bpConverterTypes::C] * vImageSize[bpConverterTypes::T];
      bpSize vImageSizeInMB = vImageSizePixels * sizeof(bpUInt8) / 1024 / 1024;
      bpString vOutputFile = vOutputFilePath;

      bpUInt8* vFileBlock = new bpUInt8[2 * vInputBlockSize];
      std::mt19937 mt(vRandSeed);
      std::normal_distribution<> dist(100.0, 40.0);
      std::uniform_int_distribution<> uniform(0, vInputBlockSize);
      double vPrevious = dist(mt);
      bpFloat vCorrelationCoefficient = 0.7f;
      for (bpSize vVoxelIndex = 0; vVoxelIndex < 2 * vInputBlockSize; ++vVoxelIndex) {
        double vRandom = (1 - vCorrelationCoefficient) * dist(mt) + vCorrelationCoefficient * vPrevious;
        vFileBlock[vVoxelIndex] = vRandom > 0 ? (vRandom < (1 << 12) ? vRandom : (1 << 12)) : 0;
      }
      bpUInt64 vFrequency = PerformanceFrequency();
      bpUInt64 vStartTime = 0;
      bpUInt64 vEndTime = vStartTime;
      bpSize vTimeInMilliSeconds = 0;

      {
        std::cout << "Input block size XYZCT: " << vInputBlockSize5D[bpConverterTypes::X] << " " << vInputBlockSize5D[bpConverterTypes::Y] << " " <<
          vInputBlockSize5D[bpConverterTypes::Z] << " " << vInputBlockSize5D[bpConverterTypes::C] << " " << vInputBlockSize5D[bpConverterTypes::T] << std::endl;

        vStartTime = PerformanceCounter();
        bpImageConverter<bpUInt8> vImageConverter(
          vImageDataType, vImageSize, vSample, vDimensionSequence, vInputBlockSize5D,
          vOutputFile, vOptions, "ImarisWriterTest", "1.0", vProgressCallback);
        bpConverterTypes::tIndex5D vBlockIndex(bpConverterTypes::X, 0, bpConverterTypes::Y, 0, bpConverterTypes::Z, 0, bpConverterTypes::C, 0, bpConverterTypes::T, 0);
        for (bpSize vIndex = 0; vIndex < vNBlocks; vIndex++) {
          bpSize vRandomOffset = uniform(mt);
          vImageConverter.CopyBlock(vFileBlock + vRandomOffset, vBlockIndex);
        }

        bpConverterTypes::tColorInfoVector vColorInfoPerChannel;
        bpConverterTypes::tTimeInfoVector vTimeInfoPerTimePoint;
        bpConverterTypes::tParameters vParameters;

        for (bpSize vChannelId = 0; vChannelId < vImageSize[bpConverterTypes::C]; ++vChannelId) {
          vColorInfoPerChannel.push_back(bpConverterTypes::cColorInfo());
        }
        vImageConverter.Finish(vImageExtent, vParameters, vTimeInfoPerTimePoint, vColorInfoPerChannel, false);

        vEndTime = PerformanceCounter();
        vTimeInMilliSeconds = (vEndTime - vStartTime) * 1000 / vFrequency;
      }

      std::cout << "Writer: " << "  MB: " << vImageSizeInMB << "     Time[ms]: " << vTimeInMilliSeconds << "\n";

      delete[] vFileBlock;

      //Sleep(500);
    } else
    if (vDataType == bpString("32bit")) {
      std::cout << "Starting writer test "  << " using " << vNumberOfThreads << " thread(s)" << std::endl;

      bpConverterTypes::cImageExtent vImageExtent{ 0,0,0,10,10,10 };
      bpConverterTypes::tDataType vImageDataType = bpConverterTypes::bpUInt32Type;
      bpConverterTypes::tDimensionSequence5D vDimensionSequence(bpConverterTypes::X, bpConverterTypes::Y, bpConverterTypes::Z, bpConverterTypes::C, bpConverterTypes::T);
      //bpConverterTypes::tDimensionSequence5D vDimensionSequence(bpConverterTypes::X, bpConverterTypes::Y, bpConverterTypes::Z, bpConverterTypes::C, bpConverterTypes::T);
      bpConverterTypes::tSize5D vSample(bpConverterTypes::X, 1, bpConverterTypes::Y, 1, bpConverterTypes::Z, 1, bpConverterTypes::C, 1, bpConverterTypes::T, 1);
      //bpConverterTypes::tSize5D vInputBlockSize5D(bpConverterTypes::X, 256, bpConverterTypes::Y, 64, bpConverterTypes::Z, 32, bpConverterTypes::C, 1, bpConverterTypes::T, 1);
      bpConverterTypes::tSize5D vInputBlockSize5D(bpConverterTypes::X, vChunkSizeX, bpConverterTypes::Y, vChunkSizeY, bpConverterTypes::Z, vChunkSizeZ, bpConverterTypes::C, vChunkSizeC, bpConverterTypes::T, vChunkSizeT);
      bpSize vInputBlockSize = vInputBlockSize5D[bpConverterTypes::X] * vInputBlockSize5D[bpConverterTypes::Y] * vInputBlockSize5D[bpConverterTypes::Z] * vInputBlockSize5D[bpConverterTypes::C] * vInputBlockSize5D[bpConverterTypes::T];
      bpSize vNBlocksX = (vImageSize[bpConverterTypes::X] - 1) / vInputBlockSize5D[bpConverterTypes::X] + 1;
      bpSize vNBlocksY = (vImageSize[bpConverterTypes::Y] - 1) / vInputBlockSize5D[bpConverterTypes::Y] + 1;
      bpSize vNBlocksZ = (vImageSize[bpConverterTypes::Z] - 1) / vInputBlockSize5D[bpConverterTypes::Z] + 1;
      bpSize vNBlocksC = (vImageSize[bpConverterTypes::C] - 1) / vInputBlockSize5D[bpConverterTypes::C] + 1;
      bpSize vNBlocksT = (vImageSize[bpConverterTypes::T] - 1) / vInputBlockSize5D[bpConverterTypes::T] + 1;
      bpSize vNBlocks = vNBlocksX * vNBlocksY * vNBlocksZ * vNBlocksC * vNBlocksT;
      bpSize vImageSizePixels = vImageSize[bpConverterTypes::X] * vImageSize[bpConverterTypes::Y] * vImageSize[bpConverterTypes::Z] * vImageSize[bpConverterTypes::C] * vImageSize[bpConverterTypes::T];
      bpSize vImageSizeInMB = vImageSizePixels * sizeof(bpUInt32) / 1024 / 1024;
      bpString vOutputFile = vOutputFilePath;

      bpUInt32* vFileBlock = new bpUInt32[2 * vInputBlockSize];
      std::mt19937 mt(vRandSeed);
      std::normal_distribution<> dist(3000.0, 400.0);
      std::uniform_int_distribution<> uniform(0, vInputBlockSize);
      double vPrevious = dist(mt);
      bpFloat vCorrelationCoefficient = 0.7f;
      for (bpSize vVoxelIndex = 0; vVoxelIndex < 2 * vInputBlockSize; ++vVoxelIndex) {
        double vRandom = (1 - vCorrelationCoefficient) * dist(mt) + vCorrelationCoefficient * vPrevious;
        vFileBlock[vVoxelIndex] = vRandom > 0 ? (vRandom < (1 << 12) ? vRandom : (1 << 12)) : 0;
      }
      bpUInt64 vFrequency = PerformanceFrequency();
      bpUInt64 vStartTime = 0;
      bpUInt64 vEndTime = vStartTime;
      bpSize vTimeInMilliSeconds = 0;

      {
        std::cout << "Input block size XYZCT: " << vInputBlockSize5D[bpConverterTypes::X] << " " << vInputBlockSize5D[bpConverterTypes::Y] << " " <<
          vInputBlockSize5D[bpConverterTypes::Z] << " " << vInputBlockSize5D[bpConverterTypes::C] << " " << vInputBlockSize5D[bpConverterTypes::T] << std::endl;

        vStartTime = PerformanceCounter();
        bpImageConverter<bpUInt32> vImageConverter(
          vImageDataType, vImageSize, vSample, vDimensionSequence, vInputBlockSize5D,
          vOutputFile, vOptions, "ImarisWriterTest", "1.0", vProgressCallback);
        bpConverterTypes::tIndex5D vBlockIndex(bpConverterTypes::X, 0, bpConverterTypes::Y, 0, bpConverterTypes::Z, 0, bpConverterTypes::C, 0, bpConverterTypes::T, 0);
        for (bpSize vIndex = 0; vIndex < vNBlocks; vIndex++) {
          bpSize vRandomOffset = uniform(mt);
          vImageConverter.CopyBlock(vFileBlock + vRandomOffset, vBlockIndex);
        }

        bpConverterTypes::tColorInfoVector vColorInfoPerChannel(vImageSize[bpConverterTypes::C]);
        bpConverterTypes::tTimeInfoVector vTimeInfoPerTimePoint;
        bpConverterTypes::tParameters vParameters;

        vImageConverter.Finish(vImageExtent, vParameters, vTimeInfoPerTimePoint, vColorInfoPerChannel, false);

        vEndTime = PerformanceCounter();
        vTimeInMilliSeconds = (vEndTime - vStartTime) * 1000 / vFrequency;
      }

      std::cout << "Writer: "  << "  MB: " << vImageSizeInMB << "     Time[ms]: " << vTimeInMilliSeconds << "\n";

      delete[] vFileBlock;

      //Sleep(500);
    }
    else {
      std::cout << "could run test here";
      //RunTests<bpUInt8>(vRuns, vSizeX, vSizeY, vSizeZ, vSizeT, vSizeC, vLogFilePath, vOutputFilePath, vIOSystem, vMultiresolution);
    }

  }
  catch (bpArgumentException& err) {
    std::cout << err.what() << std::endl;
  }

  return 0;
}


