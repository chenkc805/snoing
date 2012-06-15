#!/usr/bin/env python
# Author P G Jones - 16/05/2012 <p.g.jones@qmul.ac.uk> : First revision
#        O Wasalski - 05/06/2012 <wasalski@berkeley.edu> : Added curl dependency to RatReleasePost3
# The RAT packages base class
import LocalPackage
import os
import PackageUtil
import getpass

class Rat( LocalPackage.LocalPackage ):
    """ Base rat installer for rat."""
    def __init__( self, name ):
        super( Rat, self ).__init__( name )
        return
    def CheckState( self ):
        """ Check if rat is downloaded and installed."""
        if self._IsDownloaded:
            self._SetMode( 1 )
        if self._IsInstalled:
            self._SetMode( 2 )
        return
    def _IsInstalled( self ):
        """ Rat releases and dev share a common install check."""
        # Check rat, root, RATLib and RATDSLib
        sys = os.uname()[0]
        return os.path.exists( os.path.join( self.GetInstallPath(), "bin/rat_%s-g++" % sys ) ) \
            and os.path.exists( os.path.join( self.GetInstallPath(), "bin/root" ) ) \
            and os.path.exists( os.path.join( self.GetInstallPath(), "lib/librat_%s-g++.a" % sys ) ) \
            and os.path.exists( os.path.join( self.GetInstallPath(), "lib/libRATEvent_%s-g++.so" % sys ) )
    def _Install( self ):
        """ Derived classes should override this to install the package, should install only when finished. Return True on success."""
        self._WriteEnvFile()
        # Write the command file and source it...
        commandText = """#!/bin/bash
source %s
cd %s
./configure
source env.sh
scons""" % ( os.path.join( PackageUtil.kInstallPath, "env_%s.sh" % self._Name ), self.GetInstallPath() )
        self._InstallPath += PackageUtil.ExecuteComplexCommand( commandText )
        return


class RatRelease( Rat ):
    """ Base rat installer for rat releases."""
    def __init__( self, name, tarName ):
        """ Initialise rat with the tarName."""
        super( RatRelease, self ).__init__( name )
        self._TarName = tarName
        return
    def _IsDownloaded( self ):
        """ Check if tarball has been downloaded."""
        return os.path.exists( os.path.join( PackageUtil.kCachePath, self._TarName ) )
    def SetUsernamePassword( self, username, password ):
        """ Set the username password combination required for github downloads."""
        self._Username = username
        self._Password = password
        return 
    def _Download( self ):
        """ Derived classes should override this to download the package. Return True on success."""
        if self._Username is None:
            self._Username = raw_input( "Github username:" )
        if self._Password is None:
            print "Github password:"
            self._Password = getpass.getpass()
        self._DownloadPipe += PackageUtil.DownloadFile( "https://github.com/snoplus/rat/tarball/" + self._TarName, self._Username, self._Password )
        return
    def _Install( self ):
        """ Release installs must untar first."""
        self._InstallPipe += PackageUtil.UnTarFile( self._TarName, self.GetInstallPath(), 1 ) # Strip the first directory
        super( RatRelease, self )._Install()
        return

class RatReleasePost3( RatRelease ):
    """ Base rat installer for releases post 3.0."""
    def __init__( self, name, tarName, clhepDep, geantDep, rootDep, sconsDep, avalancheDep, zeromqDep, xercescDep, curlDep ):
        """ Initialise the rat package."""
        super( RatReleasePost3, self ).__init__( name, tarName )
        self._ClhepDependency = clhepDep
        self._GeantDependency = geantDep
        self._RootDependency = rootDep
        self._SconsDependency = sconsDep
        self._AvalancheDependency = avalancheDep
        self._ZeromqDependency = zeromqDep
        self._XercescDependency = xercescDep
        self._CurlDependency = curlDep
        return
    def GetDependencies( self ):
        """ Return the dependency names as a list of names."""
        return [ self._ClhepDependency, self._GeantDependency, self._RootDependency, \
                     self._SconsDependency, self._AvalancheDependency, self._ZeromqDependency, self._XercescDependency, self._CurlDependency ]
    def _WriteEnvFile( self ):
        """ Write the environment file for rat."""
        outText = """#!/bin/bash
#ratcage environment
source %(Geant)s/env.sh
export ROOTSYS=%(Root)s
export AVALANCHEROOT=%(Avalanche)s
export ZEROMQROOT=%(Zeromq)s
export XERCESCROOT=%(Xercesc)s
export PATH=%(Root)s/bin:%(Curl)s/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%(Clhep)s/lib:%(Root)s/lib:%(Avalanche)s/lib/cpp:%(Zeromq)s/lib:%(Xercesc)s/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:%(Clhep)s/lib:%(Root)s/lib:%(Avalanche)s/lib/cpp:%(Zeromq)s/lib:%(Xercesc)s/lib
export PYTHONPATH=%(Root)s/lib:$PYTHONPATH
export RAT_SCONS=%(Scons)s
source %(Rat)s/env.sh""" % { "Geant" : self._DependencyPaths[self._GeantDependency], "Root" : self._DependencyPaths[self._RootDependency], "Clhep" : self._DependencyPaths[self._ClhepDependency], "Scons" : self._DependencyPaths[self._SconsDependency], "Rat" : self.GetInstallPath(), "Avalanche" : self._DependencyPaths[self._AvalancheDependency], "Zeromq" : self._DependencyPaths[self._ZeromqDependency], "Xercesc" : self._DependencyPaths[self._XercescDependency], "Curl" : self._DependencyPaths[self._CurlDependency] }
        with open( os.path.join( PackageUtil.kInstallPath, "env_%s.sh" % self._Name ), "w" ) as envFile:
            envFile.write( outText )
        return

class RatReleasePre3( RatRelease ):
    """ Base rat installer for releases pre 3.0."""
    def __init__( self, name, tarName, clhepDependency, geantDependency, rootDependency, sconsDependency ):
        """ Initialise the rat package."""
        super( RatReleasePre3, self ).__init__( name, tarName )
        self._ClhepDependency = clhepDependency
        self._GeantDependency = geantDependency
        self._RootDependency = rootDependency
        self._SconsDependency = sconsDependency
        return
    def GetDependencies( self ):
        """ Return the dependency names as a list of names."""
        return [ self._ClhepDependency, self._GeantDependency, self._RootDependency, self._SconsDependency ]
    def _WriteEnvFile( self ):
        """ Write the environment file for rat."""
        outText = """#!/bin/bash
#ratcage environment
source %(Geant)s/env.sh
export ROOTSYS=%(Root)s
export PATH=%(Root)s/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%(Clhep)s/lib:%(Root)s/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:%(Clhep)s/lib:%(Root)s/lib
export PYTHONPATH=%(Root)s/lib:$PYTHONPATH
export RAT_SCONS=%(Scons)s
source %(Rat)s/env.sh""" % { "Geant" : self._DependencyPaths[self._GeantDependency], "Root" : self._DependencyPaths[self._RootDependency], "Clhep" : self._DependencyPaths[self._ClhepDependency], "Scons" : self._DependencyPaths[self._SconsDependency], "Rat" : self.GetInstallPath() }
        with open( os.path.join( PackageUtil.kInstallPath, "env_%s.sh" % self._Name ), "w" ) as envFile:
            envFile.write( outText )
        return