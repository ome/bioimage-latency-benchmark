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
#include <iostream>
#include <sstream>
#include <iomanip>
#include <map>
#include <vector>


typedef int bpInt32;
typedef size_t bpSize;
typedef float bpFloat;

using bpString = std::string;

using bpException = std::exception;
using bpArgumentException = std::runtime_error;


template <class Type>
static inline void bpFromString(const bpString& aString, Type& aResult)
{
  std::istringstream i(aString);
  i >> aResult;
}

static inline void bpFromString(const bpString& aString, bpString& aResult)
{
  aResult = aString;
}


class bpBCommandLine
{
public:
  /**
   * Constructor defines all possible arguments.
   *
   * @param argDesc Array of bpCLArgument
   * @param nargs  number of arguments
   */
  bpBCommandLine(int nInFiles, int nOutFiles)
    :requiresInFile(nInFiles != 0),
     requiresOutFile(nOutFiles != 0)
  {

  };


  void allowArgument(bpString name, bpString help, int reqNValues)
  {

    argMap.insert(std::make_pair(name,Argument(name,help,reqNValues)));

  }

  /**
   * Parses the command line, reading values, filenames and
   * performing error checking.
   *
   * @param argc
   * @param argv
   */
  void  Parse(int argc, char* argv[])
  {

    Argument* argument;
    bpString argString,valString;
    bpString err;
    int i;

    ProgName = bpString(argv[0]);

    // walk through arguments and create a new key when argument begins with "-"
    for (i = 1; i<argc; i++) {

      argString = argv[i];
      if (argString[0] == '-') {
        argString.erase(0,1);

        if (argMap.count(argString) == 1) {   // argument is ok

          argument=&(argMap[argString]);
          argument->SetFound(true);

          // check whether argument should have a value. If so, read it.
          if (argument->RequiredNumberOfValues()==1) {
            if (argv[i+1][0] != '-') {
              argument->SetValue(argv[i+1]);
              i++;
            }
            else {
              err.append("Argument '");
              err.append(argString);
              err.append("' requires a value.");
              throw bpArgumentException(err);
            }
          }
        }
        else {
          if (argString == "h") {
            PrintUsage();
            throw bpArgumentException("");
          }
          PrintUsage();
          err.append("Unknown command line argument '");
          err.append(argString);
          err.append("' .");
          throw bpArgumentException(err);
        }

      }
      else { // it is a filename
        inFileNames.push_back(argv[i]);
      }

    }

    if (inFileNames.empty() && (requiresInFile || requiresOutFile)) {
    }
    if (inFileNames.size() == 1 && (requiresInFile && requiresOutFile)) {
    }
    if (requiresOutFile && inFileNames.size()>0) {
      // last filename is outfile
      outFileName = *(inFileNames.end()-1);
      inFileNames.erase(inFileNames.end()-1);
    }
  }


  /**
    * Returns true if the argument was found in the command line
    * and false if not.
    *
    * @param name
    * @return
    */
  bool Found(const bpString name)
  {
    return argMap[name].Found();
  }


  void GetValue(const bpString& name, bpString& value)
  {

    if (Found(name)) {
      value = argMap[name].GetValue();
    }
    else {
      bpString err;
      err.append("Missing argument '");
      err.append(name);
      err.append("'");
      throw bpArgumentException(err);
    }

  }

  void GetValue(const bpString& name, bpInt32& value)
  {

    if (Found(name)) {
      bpFromString(argMap[name].GetValue(),value);
    }
    else {
      bpString err;
      err.append("Missing argument '");
      err.append(name);
      err.append("'");
      throw bpArgumentException(err);
    }
  }

  void GetValue(const bpString& name, bpSize& value)
  {
    if (Found(name)) {
      bpFromString(argMap[name].GetValue(),value);
    }
    else {
      bpString err;
      err.append("Missing argument '");
      err.append(name);
      err.append("'");
      throw bpArgumentException(err);
    }
  }

  void GetValue(const bpString& name, bpFloat& value)
  {

    if (Found(name)) {
      bpFromString(argMap[name].GetValue(),value);
    }
    else {
      bpString err;
      err.append("Missing argument '");
      err.append(name);
      err.append("'");
      throw bpArgumentException(err);
    }

  }

  void GetValue(const bpString& name, bool& value)
  {

    bpString v = argMap[name].GetValue();

    if (Found(name)) {
      if (v == "true" || v == "on") {
        value = true;
      }
      else {
        if (v == "false" || v == "off") {
          value = false;
        }
        else {
          bpString err;
          err.append("Invalid value for '");
          err.append(name);
          err.append("'");
          throw bpArgumentException(err);
        }
      }
    }
    else {
      bpString err;
      err.append("Missing argument '");
      err.append(name);
      err.append("'");
      throw bpArgumentException(err);
    }

  }

  void PrintUsage()
  {

    std::map<bpString,Argument>::iterator it = argMap.begin();

    std::cout << std::endl << "Usage: " << ProgName.c_str() << " [Options] ";
    if (requiresInFile) {
      std::cout << "inFile(s) ";
    }
    if (requiresOutFile) {
      std::cout << "outFile ";
    }
    std::cout << std::endl;
    std::cout << std::endl << "where Options are:" << std::endl;

    while (it != argMap.end()) {
      bpString option((*it).first);
      int l = static_cast<bpInt32>(option.size());
      while (l++<12) {
        option.append(".");
      }
      std::cout << "              -" << option.c_str() << "  " <<  (*it).second.GetHelp().c_str() << std::endl;
      ++it;
    }
  }

  void PrintOptions()
  {

    std::map<bpString,Argument>::iterator it = argMap.begin();

    while (it != argMap.end()) {
      std::cout << "              -" << (*it).first.c_str() << "  " <<  (*it).second.GetHelp().c_str() << std::endl;
      ++it;
    }
  }


  /**
   * Returns all strings that were interpreted as inFileNames.
   * The rules are: any string on the command line that does
   * not begin with "-" and is not a value of the previous
   * argument is a filename.  The last filename is the
   * outFileName, all others are inFileNames.
   *
   * @return
   */
  std::vector<bpString> GetInFileNames()
  {
    return inFileNames;
  }

  /**
   * returns file name of first input file.
   * (convenience function)
   *
   * @return filename as bpString
   */
  bpString GetFirstInFileName()
  {
    return inFileNames[0];
  }

  bpString GetOutFileName()
  {
    return outFileName;
  }


  /**
   * Internal Class to hold everything that belongs to one
   * command line argument.
   */
  class Argument
  {
  public:

    Argument()
    {
    }

    Argument(bpString name, bpString helpString, int reqNValues)
      : argName(name),
        help(helpString),
        nRequiredValues(reqNValues),
        found(false)
    {

    }

    bpString GetName()
    {
      return argName;
    }

    void SetName(bpString name)
    {
      argName = name;
    }

    bpString GetHelp()
    {
      return help;
    }

    void SetHelp(bpString helpString)
    {
      help = helpString;
    }


    bpString GetValue()
    {
      return valString;
    }

    void SetValue(bpString value)
    {
      valString = value;
    }

    int RequiredNumberOfValues()
    {
      return nRequiredValues;
    }


    bool Found()
    {
      return found;
    }

    void SetFound(bool argFound)
    {
      found = argFound;
    }

  private:
    bpString argName;
    bpString valString;
    bpString help;
    int nRequiredValues;
    bool found;
  };

  bpString ProgName;

  bool requiresInFile;
  bool requiresOutFile;

  std::vector<bpString> inFileNames;
  bpString outFileName;

  std::map<bpString,Argument> argMap;
};


