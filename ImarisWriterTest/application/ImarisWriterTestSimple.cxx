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
#include "imariswriter/interface/bpConverterTypes.h"
#include "imariswriter/interface/bpImageConverter.h"
#include <iostream>

using namespace bpConverterTypes;

void RecordProgress(bpFloat aProgress, bpFloat aTP) {std::cout << "Progress: " << aProgress*100 << "%\n";}

int main(int argc, char* argv[])
{
  tSize5D vImageSize(X, 2048, Y, 2048, Z, 100, C, 3, T, 1);
  tDimensionSequence5D vBlockDimensionSequence(X, Y, Z, C, T);
  tSize5D vBlockSize5D(X, 512, Y, 512, Z, 1, C, 1, T, 1);
  tSize5D vSample(X, 1, Y, 1, Z, 1, C, 1, T, 1);
  bpSize vBlockSize = vBlockSize5D[X] * vBlockSize5D[Y] * vBlockSize5D[Z];
  bpString vOutputFile = "C:\\ImarisWriterTest\\ImarisWriterTest.ims";
  cOptions vOptions;
  vOptions.mNumberOfThreads = 12;
  vOptions.mCompressionAlgorithmType = eCompressionAlgorithmGzipLevel2;

  bpUInt16* vFileBlock = new bpUInt16[vBlockSize];
  for (bpSize vVoxelIndex = 0; vVoxelIndex < vBlockSize; ++vVoxelIndex) {
    vFileBlock[vVoxelIndex] = vVoxelIndex % 512;
  }

  bpImageConverter<bpUInt16> vImageConverter(bpUInt16Type, vImageSize, vSample,
     vBlockDimensionSequence, vBlockSize5D, vOutputFile, vOptions, "ImarisWriterTest", "1.0", RecordProgress);

  for (bpSize vIndexT = 0; vIndexT < (vImageSize[T] - 1) / vBlockSize5D[T] + 1; vIndexT++) {
    for (bpSize vIndexC = 0; vIndexC < (vImageSize[C] - 1) / vBlockSize5D[C] + 1; vIndexC++) {
      for (bpSize vIndexZ = 0; vIndexZ < (vImageSize[Z] - 1) / vBlockSize5D[Z] + 1; vIndexZ++) {
        for (bpSize vIndexY = 0; vIndexY < (vImageSize[Y] - 1) / vBlockSize5D[Y] + 1; vIndexY++) {
          for (bpSize vIndexX = 0; vIndexX < (vImageSize[X] - 1) / vBlockSize5D[X] + 1; vIndexX++) {
            vImageConverter.CopyBlock(vFileBlock, {{X, vIndexX }, {X,  vIndexY}, {Z, vIndexZ}, {C, vIndexC}, {T, vIndexT}
          });
          }
        }
      }
    }
  }

  tColorInfoVector vColorInfoPerChannel(vImageSize[C]);
  tTimeInfoVector vTimeInfoPerTimePoint;
  tParameters vParameters; vParameters["Image"]["ImageSizeInMB"] = "2400";
  vImageConverter.Finish({ 0,0,0,10,10,10 }, vParameters, vTimeInfoPerTimePoint, vColorInfoPerChannel, false);
  delete vFileBlock;
  return 0;
}
