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
 
/*
gcc -I. -L. -o bpImarisWriter96TestProgram.exe bpImarisWriter96TestProgram.c -lbpImarisWriter96
./bpImarisWriter96TestProgram.exe
*/

#include "bpImageConverterInterfaceC.h"

#include <stdio.h>
#include <stdlib.h>


typedef struct
{
  unsigned int mImageIndex;
  int mProgress;
} bpCallbackData;

void ProgressCallback(bpConverterTypesC_Float aProgress, bpConverterTypesC_UInt64 aTotalBytesWritten, void* aUserData)
{
  bpCallbackData* vCallbackData = (bpCallbackData*)aUserData;

  int vProgress = (int)(aProgress * 100);
  if (vProgress - vCallbackData->mProgress < 5) {
    return;
  }

  unsigned int vImageIndex = vCallbackData->mImageIndex;
  if (aTotalBytesWritten < 10 * 1024 * 1024) {
    printf("Progress image %u: %d%% [%llu KB]\n", vImageIndex, vProgress, aTotalBytesWritten / 1024);
  }
  else {
    printf("Progress image %u: %d%% [%llu MB]\n", vImageIndex, vProgress, aTotalBytesWritten / (1024 * 1024));
  }
  vCallbackData->mProgress = vProgress;
}

unsigned int NumBlocks(unsigned int aSize, unsigned int aBlockSize)
{
    return (aSize + aBlockSize - 1) / aBlockSize;
}

void CheckErrors(bpImageConverterCPtr aConverter)
{
  const char* vException = bpImageConverterC_GetLastException(aConverter);
  if (vException) {
    printf("%s", vException);
    exit(1);
  }
}

void TestConvert(unsigned int aTestIndex)
{
  bpConverterTypesC_DataType aDataType = bpConverterTypesC_UInt8Type;
  bpConverterTypesC_Size5D aImageSize;
  aImageSize.mValueX = 512;
  aImageSize.mValueY = 512;
  aImageSize.mValueZ = 32;
  aImageSize.mValueT = 4;
  aImageSize.mValueC = 2;
  float vVoxelSizeXY = 1.4f;
  float vVoxelSizeZ = 5.4f;
  bpConverterTypesC_ImageExtent aImageExtent = {
    0, 0, 0,
    aImageSize.mValueX * vVoxelSizeXY,
    aImageSize.mValueY * vVoxelSizeXY,
    aImageSize.mValueZ * vVoxelSizeZ
  };
  bpConverterTypesC_Size5D aSample = { 1, 1, 1, 1, 1 };

  bpConverterTypesC_DimensionSequence5D aDimensionSequence = {
      bpConverterTypesC_DimensionX,
      bpConverterTypesC_DimensionY,
      bpConverterTypesC_DimensionZ,
      bpConverterTypesC_DimensionC,
      bpConverterTypesC_DimensionT
  };
  bpConverterTypesC_Size5D aBlockSize = {
      256, 256, 8, 1, 1
  };
  char aOutputFile[256];
  sprintf(aOutputFile, "./out_%d.ims", aTestIndex);

  bpConverterTypesC_Options aOptions;
  aOptions.mThumbnailSizeXY = 256;
  aOptions.mFlipDimensionX = false;
  aOptions.mFlipDimensionY = false;
  aOptions.mFlipDimensionZ = false;
  aOptions.mForceFileBlockSizeZ1 = false;
  aOptions.mEnableLogProgress = true;
  aOptions.mNumberOfThreads = 8;
  aOptions.mCompressionAlgorithmType = eCompressionAlgorithmGzipLevel2;

  bpConverterTypesC_String aApplicationName = "TestC";
  bpConverterTypesC_String aApplicationVersion = "1.0.0";
  bpConverterTypesC_ProgressCallback aProgressCallback = ProgressCallback;

  bpCallbackData aCallbackUserData;
  aCallbackUserData.mImageIndex = aTestIndex;
  aCallbackUserData.mProgress = -5;

  bpImageConverterCPtr vConverter = bpImageConverterC_Create(
    aDataType, &aImageSize, &aSample,
    &aDimensionSequence, &aBlockSize,
    aOutputFile, &aOptions,
    aApplicationName, aApplicationVersion,
    aProgressCallback, &aCallbackUserData
  );
  CheckErrors(vConverter);

  unsigned long long vBlockSize =
    (unsigned long long)aBlockSize.mValueX *
    aBlockSize.mValueY * aBlockSize.mValueZ *
    aBlockSize.mValueC * aBlockSize.mValueT;

  unsigned char* vData = malloc(vBlockSize);
  for (unsigned long long vIndex = 0; vIndex < vBlockSize; ++vIndex) {
    vData[vIndex] = (unsigned char)(vIndex % 256);
  }

  unsigned int vNBlocksX = NumBlocks(aImageSize.mValueX, aBlockSize.mValueX);
  unsigned int vNBlocksY = NumBlocks(aImageSize.mValueY, aBlockSize.mValueY);
  unsigned int vNBlocksZ = NumBlocks(aImageSize.mValueZ, aBlockSize.mValueZ);
  unsigned int vNBlocksC = NumBlocks(aImageSize.mValueC, aBlockSize.mValueC);
  unsigned int vNBlocksT = NumBlocks(aImageSize.mValueT, aBlockSize.mValueT);

  bpConverterTypesC_Index5D aBlockIndex = {
      0, 0, 0, 0, 0
  };

  for (unsigned int vC = 0; vC < vNBlocksC; ++vC) {
    aBlockIndex.mValueC = vC;
    for (unsigned int vT = 0; vT < vNBlocksT; ++vT) {
      aBlockIndex.mValueT = vT;
      for (unsigned int vZ = 0; vZ < vNBlocksZ; ++vZ) {
        aBlockIndex.mValueZ = vZ;
        for (unsigned int vY = 0; vY < vNBlocksY; ++vY) {
          aBlockIndex.mValueY = vY;
          for (unsigned int vX = 0; vX < vNBlocksX; ++vX) {
            aBlockIndex.mValueX = vX;
            bpImageConverterC_CopyBlockUInt8(vConverter, vData, &aBlockIndex);
            CheckErrors(vConverter);
          }
        }
      }
    }
  }

  free(vData);

  unsigned int vNumberOfOtherSections = 1; // Image
  unsigned int vNumberOfSections = vNumberOfOtherSections + aImageSize.mValueC;
  bpConverterTypesC_ParameterSection* vParameterSections = malloc(vNumberOfSections * sizeof(bpConverterTypesC_ParameterSection));

  bpConverterTypesC_Parameter vUnitParameter = { "Unit", "um" };
  bpConverterTypesC_ParameterSection* vImageSection = &vParameterSections[0];
  vImageSection->mName = "Image";
  vImageSection->mValuesCount = 1;
  vImageSection->mValues = &vUnitParameter;

  char vChannelNamesBuffer[1024]; // will this be enough?
  char* vChannelNameBuffer = vChannelNamesBuffer;
  
  unsigned int vNumberOfParametersPerChannel = 3;
  bpConverterTypesC_Parameter* vChannelParameters = malloc(aImageSize.mValueC * vNumberOfParametersPerChannel * sizeof(bpConverterTypesC_Parameter));
  for (unsigned int vC = 0; vC < aImageSize.mValueC; ++vC) {
    bpConverterTypesC_Parameter* vThisChannelParameters = &vChannelParameters[vNumberOfParametersPerChannel * vC];
    vThisChannelParameters[0].mName = "Name";
    vThisChannelParameters[0].mValue = vC == 0 ? "First channel" : vC == 1 ? "Second channel" : vC == 2 ? "Third channel" : "Other channel";
    vThisChannelParameters[1].mName = "LSMEmissionWavelength";
    vThisChannelParameters[1].mValue = "700";
    vThisChannelParameters[2].mName = "OtherChannelParameter";
    vThisChannelParameters[2].mValue = "OtherChannelValue";
    bpConverterTypesC_ParameterSection* vChannelSection = &vParameterSections[vNumberOfOtherSections + vC];
    int vChannelNameLength = sprintf(vChannelNameBuffer, "Channel %i", vC);
    vChannelSection->mName = vChannelNameBuffer;
    vChannelNameBuffer += vChannelNameLength + 1;
    vChannelSection->mValues = vThisChannelParameters;
    vChannelSection->mValuesCount = vNumberOfParametersPerChannel;
  }

  bpConverterTypesC_Parameters aParameters;
  aParameters.mValuesCount = vNumberOfSections;
  aParameters.mValues = vParameterSections;

  bpConverterTypesC_TimeInfo* vTimeInfos = malloc(aImageSize.mValueT * sizeof(bpConverterTypesC_TimeInfo));
  for (unsigned int vT = 0; vT < aImageSize.mValueT; ++vT) {
    vTimeInfos[vT].mJulianDay = 2458885; // 5 feb 2020
    unsigned long long vSeconds = vT + 4 + 60 * (27 + 60 * 15); // 3:27.04 PM + 1 sec per time point
    vTimeInfos[vT].mNanosecondsOfDay = vSeconds * 1000000000;
  }
  bpConverterTypesC_TimeInfos aTimeInfoPerTimePoint;
  aTimeInfoPerTimePoint.mValuesCount = aImageSize.mValueT;
  aTimeInfoPerTimePoint.mValues = vTimeInfos;

  bpConverterTypesC_ColorInfo* vColorInfos = malloc(aImageSize.mValueC * sizeof(bpConverterTypesC_ColorInfo));
  for (unsigned int vC = 0; vC < aImageSize.mValueC; ++vC) {
    bpConverterTypesC_ColorInfo* vColor = &vColorInfos[vC];
    vColor->mIsBaseColorMode = true;
    vColor->mBaseColor.mRed = (vC % 3) == 0 ? 1 : 0;
    vColor->mBaseColor.mGreen = (vC % 3) == 1 ? 1 : 0;
    vColor->mBaseColor.mBlue = (vC % 3) == 2 ? 1 : 0;
    vColor->mBaseColor.mAlpha = 1;
    vColor->mColorTableSize = 0;
    vColor->mOpacity = 0;
    vColor->mRangeMin = 0;
    vColor->mRangeMax = 255;
    vColor->mGammaCorrection = 1;
  }
  bpConverterTypesC_ColorInfos aColorInfoPerChannel;
  aColorInfoPerChannel.mValuesCount = aImageSize.mValueC;
  aColorInfoPerChannel.mValues = vColorInfos;

  bool aAutoAdjustColorRange = true;

  bpImageConverterC_Finish(vConverter,
    &aImageExtent, &aParameters, &aTimeInfoPerTimePoint,
    &aColorInfoPerChannel, aAutoAdjustColorRange);
  CheckErrors(vConverter);

  free(vTimeInfos);
  free(vColorInfos);

  free(vParameterSections);
  free(vChannelParameters);

  bpImageConverterC_Destroy(vConverter);
}

int main(int argc, char* argv[])
{
  for (unsigned int vI = 0; vI < 2; ++vI) {
    TestConvert(vI);
  }
}
