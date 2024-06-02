%define __requires_exclude ^libzmusic\\.so.*|.*libgomp.*\\.so.*|.*libvpx.*\\.so.*|.*libmpg123.*\\.so.*|.*libminiz.*\\.so.*|.*libdiscord-rpc.*\\.so.*$
%define __provides_exclude_from ^%{_datadir}/%{name}/lib/.*\\.so.*$

Name   : org.zdoom.gzdoom
Version: 4.13.0
Release: 1
Summary: Doom sourceport with advanced features
License: GPLv3
URL    : https://zdoom.org
Source : %{name}-%{version}.tar.bz2

BuildRequires: bzip2-devel
BuildRequires: pkgconfig(openal)
BuildRequires: pkgconfig(wayland-client)
BuildRequires: pkgconfig(vpx)
BuildRequires: pkgconfig(libmpg123)
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(sndfile)
BuildRequires: cmake
BuildRequires: patchelf
BuildRequires: zip
BuildRequires: pkgconfig(wayland-egl)
BuildRequires: pkgconfig(wayland-cursor)
BuildRequires: pkgconfig(wayland-protocols)
BuildRequires: pkgconfig(wayland-scanner)
BuildRequires: pkgconfig(egl)
BuildRequires: pkgconfig(glesv1_cm)
BuildRequires: pkgconfig(glesv2)
BuildRequires: pkgconfig(xkbcommon)
BuildRequires: pkgconfig(libpulse-simple)

%description
%{summary}.

%prep
%autosetup

%build
%cmake \
    -Bbuild_zmusic_%{_arch} \
    -DCMAKE_BUILD_TYPE=Release \
    zmusic

pushd build_zmusic_%{_arch}
%make_build -j`nproc`
popd

%cmake \
    -Bbuild_libsdl_%{_arch} \
    -DSDL_PULSEAUDIO=OFF \
    -DSDL_RPATH=OFF \
    -DSDL_STATIC=ON \
    -DSDL_SHARED=OFF \
    -DSDL_WAYLAND=ON \
    -DSDL_X11=OFF \
    -DSDL_WAYLAND_LIBDECOR=OFF \
    libsdl

pushd build_libsdl_%{_arch}
%make_build -j`nproc`
mv include-config-/SDL2/* include/SDL2/
popd

%cmake \
    -Bbuild_gzdoom_%{_arch} \
    -DCMAKE_BUILD_TYPE=Release \
    -DNO_FMOD=ON \
    -DAURORAOS=ON \
    -DVULKAN_USE_XLIB=OFF \
    -DVULKAN_USE_WAYLAND=ON \
    -DSDL2_INCLUDE_DIR="`pwd`/build_libsdl_%{_arch}/include/SDL2" \
    -DSDL2_LIBRARY="`pwd`/build_libsdl_%{_arch}/libSDL2.a" \
    -DZMUSIC_INCLUDE_DIR="`pwd`/zmusic/include" \
    -DZMUSIC_LIBRARIES="`pwd`/build_zmusic_%{_arch}/source/libzmusic.so" \
    upstream

pushd build_gzdoom_%{_arch}
%make_build -j`nproc`
popd 


%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_datadir}/%{name}/pk3/
pushd upstream/wadsrc/static
zip -FS -r -y %{buildroot}%{_datadir}/%{name}/pk3/gzdoom.pk3 *
popd

pushd upstream/wadsrc_bm/static
zip -FS -r -y %{buildroot}%{_datadir}/%{name}/pk3/brightmaps.pk3 *
popd

pushd upstream/wadsrc_extra/static
zip -FS -r -y %{buildroot}%{_datadir}/%{name}/pk3/game_support.pk3 *
popd

pushd upstream/wadsrc_lights/static
zip -FS -r -y %{buildroot}%{_datadir}/%{name}/pk3/lights.pk3 *
popd

pushd upstream/wadsrc_widepix/static
zip -FS -r -y %{buildroot}%{_datadir}/%{name}/pk3/game_widescreen_gfx.pk3 *
popd

pushd build_gzdoom_%{_arch}
patchelf --force-rpath --set-rpath %{_datadir}/%{name}/lib gzdoom
install -m 0755 -D -s gzdoom %{buildroot}%{_bindir}/%{name}
install -m 755 -D -s libraries/discordrpc/src/libdiscord-rpc.so -t %{buildroot}%{_datadir}/%{name}/lib/
install -m 755 -D -s libraries/miniz/libminiz.so -t %{buildroot}%{_datadir}/%{name}/lib/
popd
pushd upstream/
install -m 0655 -D fm_banks/GENMIDI.GS.wopl  -t %{buildroot}%{_datadir}/%{name}/fm_banks/
install -m 0655 -D fm_banks/gs-by-papiezak-and-sneakernets.wopn -t %{buildroot}%{_datadir}/%{name}/fm_banks/
install -m 0655 -D soundfont/* -t %{buildroot}%{_datadir}/%{name}/soundfonts/
popd

install -m 0655 -D icons/86.png %{buildroot}%{_datadir}/icons/hicolor/86x86/apps/%{name}.png
install -m 0655 -D icons/108.png %{buildroot}%{_datadir}/icons/hicolor/108x108/apps/%{name}.png
install -m 0655 -D icons/128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
install -m 0655 -D icons/172.png %{buildroot}%{_datadir}/icons/hicolor/172x172/apps/%{name}.png

pushd build_zmusic_%{_arch}
install -m 755 -D -s source/libzmusic.so.1.1.10 %{buildroot}%{_datadir}/%{name}/lib/libzmusic.so.1
popd 

install -m 0655 -D %{name}.desktop -t %{buildroot}%{_datadir}/applications/
install -D %{_libdir}/libgomp.so.1* -t %{buildroot}%{_datadir}/%{name}/lib/
install -D %{_libdir}/libopenal.so.1* -t %{buildroot}%{_datadir}/%{name}/lib/
install -D %{_libdir}/libvpx.so.* -t %{buildroot}%{_datadir}/%{name}/lib/
install -D %{_libdir}/libmpg123.so.* -t %{buildroot}%{_datadir}/%{name}/lib/

%files
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/86x86/apps/%{name}.png
%{_datadir}/icons/hicolor/108x108/apps/%{name}.png
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
%{_datadir}/icons/hicolor/172x172/apps/%{name}.png
%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/*
%{_bindir}/%{name}
