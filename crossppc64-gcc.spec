Summary:	Cross PPC64 GNU binary utility development utilities - gcc
Summary(es):	Utilitarios para desarrollo de binarios de la GNU - PPC64 gcc
Summary(fr):	Utilitaires de développement binaire de GNU - PPC64 gcc
Summary(pl):	Skro¶ne narzêdzia programistyczne GNU dla PPC64 - gcc
Summary(pt_BR):	Utilitários para desenvolvimento de binários da GNU - PPC64 gcc
Summary(tr):	GNU geliþtirme araçlarý - PPC64 gcc
Name:		crossppc64-gcc
Version:	4.1.0
%define		_snap	20051230
Release:	0.%{_snap}.1
Epoch:		1
License:	GPL
Group:		Development/Languages
#Source0:	ftp://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.bz2
Source0:	ftp://gcc.gnu.org/pub/gcc/snapshots/4.1-%{_snap}/gcc-4.1-%{_snap}.tar.bz2
# Source0-md5:	f76dfdb7b6a3148ca94ebab429346729
%define		_llh_ver	2.6.12.0
Source1:	http://ep09.pld-linux.org/~mmazur/linux-libc-headers/linux-libc-headers-%{_llh_ver}.tar.bz2
# Source1-md5:	eae2f562afe224ad50f65a6acfb4252c
%define		_glibc_ver	2.3.6
Source2:	ftp://sources.redhat.com/pub/glibc/releases/glibc-%{_glibc_ver}.tar.bz2
# Source2-md5:	bfdce99f82d6dbcb64b7f11c05d6bc96
Source3:	ftp://sources.redhat.com/pub/glibc/releases/glibc-linuxthreads-%{_glibc_ver}.tar.bz2
# Source3-md5:	d4eeda37472666a15cc1f407e9c987a9
Patch0:		%{name}-libc-sysdeps-configure.patch
URL:		http://gcc.gnu.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	crossppc64-binutils
BuildRequires:	fileutils >= 4.0.41
BuildRequires:	flex
BuildRequires:	texinfo >= 4.1
Requires:	crossppc64-binutils
Requires:	gcc-dirs
ExcludeArch:	ppc64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		ppc64-pld-linux
%define		arch		%{_prefix}/%{target}
%define		gccarch		%{_libdir}/gcc/%{target}
%define		gcclib		%{gccarch}/%{version}

%define		_noautostrip	.*/libgc.*\\.a

%description
This package contains a cross-gcc which allows the creation of
binaries to be run on PPC64 Linux on other machines.

%description -l de
Dieses Paket enthält einen Cross-gcc, der es erlaubt, auf einem
anderem Rechner Code für PPC64 Linux zu generieren.

%description -l pl
Ten pakiet zawiera skro¶ny gcc pozwalaj±cy na robienie na innych
maszynach binariów do uruchamiania na Linuksie PPC64.

%package c++
Summary:	C++ support for crossppc64-gcc
Summary(pl):	Obs³uga C++ dla crossppc64-gcc
Group:		Development/Languages
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description c++
This package adds C++ support to the GNU Compiler Collection for
PPC64.

%description c++ -l pl
Ten pakiet dodaje obs³ugê C++ do kompilatora gcc dla PPC64.

%prep
#setup -q -n gcc-%{version} -a1 -a2 -a3
%setup -q -n gcc-4.1-%{_snap} -a1 -a2 -a3
mv linuxthreads* glibc-%{_glibc_ver}
%patch0 -p1

%build
FAKE_ROOT=$PWD/fake-root

rm -rf $FAKE_ROOT && install -d $FAKE_ROOT%{_includedir}
cp -r linux-libc-headers-%{_llh_ver}/include/{asm-ppc64,linux} $FAKE_ROOT%{_includedir}
ln -s asm-ppc64 $FAKE_ROOT%{_includedir}/asm

cd glibc-%{_glibc_ver}
cp -f /usr/share/automake/config.* scripts
rm -rf builddir && install -d builddir && cd builddir
../configure \
--prefix=$FAKE_ROOT%{_prefix} \
	--build=%{_target_platform} \
	--host=%{target} \
	--disable-nls \
	--enable-add-ons=linuxthreads \
	--with-headers=$FAKE_ROOT%{_includedir} \
	--disable-sanity-checks \
	--enable-hacker-mode

%{__make} sysdeps/gnu/errlist.c
%{__make} install-headers

install bits/stdio_lim.h $FAKE_ROOT%{_includedir}/bits
touch $FAKE_ROOT%{_includedir}/gnu/stubs.h
cd ../..

cp -f /usr/share/automake/config.* .
rm -rf obj-%{target}
install -d obj-%{target}
cd obj-%{target}

CFLAGS="%{rpmcflags}" \
CXXFLAGS="%{rpmcflags}" \
TEXCONFIG=false \
../configure \
	--prefix=%{_prefix} \
	--infodir=%{_infodir} \
	--mandir=%{_mandir} \
	--bindir=%{_bindir} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libdir} \
	--disable-shared \
	--disable-threads \
	--enable-languages="c,c++" \
	--enable-c99 \
	--enable-long-long \
	--disable-nls \
	--with-gnu-as \
	--with-gnu-ld \
	--with-demangler-in-ld \
	--with-system-zlib \
	--enable-multilib \
	--with-headers=$FAKE_ROOT%{_includedir} \
	--without-x \
	--target=%{target} \
	--host=%{_target_platform} \
	--build=%{_target_platform}

%{__make} all-gcc

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C obj-%{target} install-gcc \
	DESTDIR=$RPM_BUILD_ROOT

install obj-%{target}/gcc/specs $RPM_BUILD_ROOT%{gcclib}

# don't want this here
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty.a

# include/ contains install-tools/include/* and headers that were fixed up
# by fixincludes, we don't want former
gccdir=$RPM_BUILD_ROOT%{gcclib}
mkdir	$gccdir/tmp
# we have to save these however
mv -f	$gccdir/include/syslimits.h $gccdir/tmp
rm -rf	$gccdir/include
mv -f	$gccdir/tmp $gccdir/include
cp -f	$gccdir/install-tools/include/*.h $gccdir/include
# but we don't want anything more from install-tools
rm -rf	$gccdir/install-tools

%if 0%{!?debug:1}
%{target}-strip -g -R.note -R.comment $RPM_BUILD_ROOT%{gcclib}/libgcc.a
%{target}-strip -g -R.note -R.comment $RPM_BUILD_ROOT%{gcclib}/libgcov.a
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-gcc
%attr(755,root,root) %{_bindir}/%{target}-cpp
%dir %{gccarch}
%dir %{gcclib}
%attr(755,root,root) %{gcclib}/cc1
%attr(755,root,root) %{gcclib}/collect2
%dir %{gcclib}/32
%{gcclib}/32/crt*.o
%{gcclib}/32/libgcc.a
%{gcclib}/crt*.o
%{gcclib}/libgcc.a
%{gcclib}/specs*
%dir %{gcclib}/include
%{gcclib}/include/*.h
%{_mandir}/man1/%{target}-cpp.1*
%{_mandir}/man1/%{target}-gcc.1*

%files c++
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-g++
%attr(755,root,root) %{gcclib}/cc1plus
%{_mandir}/man1/%{target}-g++.1*
