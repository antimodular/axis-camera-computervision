ARG ARCH=armv7hf
ARG REPO=axisecp
ARG SDK=acap-native-sdk
ARG UBUNTU_VERSION=20.04
ARG VERSION=1.1

#-- Build configuration --#
# ARCH_CFLAGS is supplied as a compile option
ARG ARCH_CFLAGS="-O2 -mthumb -mfpu=neon -mfloat-abi=hard -mcpu=cortex-a9 -fomit-frame-pointer"
# AXIS_ARCH is the AXIS platform descriptor
ARG AXIS_ARCH=armv7hf
# BUILD_ROOT defines where in the build containers the building takes place
ARG BUILD_ROOT=/build-root
# DOCKERHUB_ARCH is the DockerHub platform descriptor
ARG DOCKERHUB_ARCH=arm32v7
# OPENCV_MODULES defines what OpenCV modules to build
ARG OPENCV_MODULES=core,imgproc,imgcodecs,videoio,objdetect,python3,video,feature2d 
# SDK_ROOT_DIR defines the root directory of the final SDK images
ARG SDK_ROOT_DIR=/axis/
# UBUNTU_ARCH is the Ubuntu platform descriptor
ARG UBUNTU_ARCH=armhf
# TARGET_TOOLCHAIN is the name of the compilation toolchain for the target platform
ARG TARGET_TOOLCHAIN=arm-linux-gnueabihf
# TARGET_ROOT defines where in the build containers the resulting application is put
ARG TARGET_ROOT=/target-root
# UBUNTU_VERSION defines the ubuntu version of the build and SDK containers
ARG UBUNTU_VERSION=20.04
# UBUNTU_CODENAME should be the ubuntu codename of the UBUNTU_VERSION used, e.g., focal, hirsute, ..
ARG UBUNTU_CODENAME=focal

#-- Versions of installed packages defined as repository tags --#
ARG NUMPY_VERSION=v1.17.3
ARG OPENBLAS_VERSION=v0.3.14
ARG OPENCV_VERSION=4.5.1
ARG PYTESSERACT_VERSION=0.3.7
ARG SCIPY_VERSION=v1.7.1
ARG TESSERACT_VERSION=4.1.1
ARG TFSERVING_VERSION=2.0.0

#-- Build parallelization  --#
ARG OPENBLAS_BUILD_CORES=16
ARG OPENCV_BUILD_CORES=16

#-- ACAP SDK configuration --#
ARG REPO=axisecp
ARG ACAP_SDK_IMAGE=acap-native-sdk
ARG ACAP_SDK_UBUNTU_VERSION=20.04
ARG ACAP_SDK_VERSION=1.1
ARG ACAP_SDK_TAG=${ACAP_SDK_VERSION}-${AXIS_ARCH}-ubuntu${ACAP_SDK_UBUNTU_VERSION}

# The ACAP Native SDK is used to get certain libs and headers
FROM ${REPO}/${ACAP_SDK_IMAGE}:${ACAP_SDK_TAG} AS acap-native-sdk
# libs: /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/lib/
# headers: /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/include/

# Create a base image with build tools, env vars, etc.,
FROM ubuntu:${UBUNTU_VERSION} AS build-base

# Setup environment variables
ENV DEBIAN_FRONTEND=noninteractive
ARG BUILD_ROOT
ARG TARGET_TOOLCHAIN
ARG TARGET_ROOT
ARG UBUNTU_ARCH
ARG UBUNTU_CODENAME
ARG http_proxy
ARG https_proxy

# To support DOCKER_BUILDKIT=0, base ARGs are converted to ENVs to allow propagation
ENV BUILD_ROOT=$BUILD_ROOT
ENV TARGET_TOOLCHAIN=$TARGET_TOOLCHAIN
ENV TARGET_ROOT=$TARGET_ROOT
ENV UBUNTU_ARCH=$UBUNTU_ARCH
ENV UBUNTU_CODENAME=$UBUNTU_CODENAME
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

# Add source for target arch
RUN echo \
"deb [arch=amd64] http://us.archive.ubuntu.com/ubuntu/ $UBUNTU_CODENAME main restricted universe multiverse\n\
deb [arch=amd64] http://us.archive.ubuntu.com/ubuntu/ $UBUNTU_CODENAME-updates main restricted universe multiverse\n\
deb [arch=amd64] http://us.archive.ubuntu.com/ubuntu/ $UBUNTU_CODENAME-backports main restricted universe multiverse\n\
deb [arch=amd64] http://security.ubuntu.com/ubuntu $UBUNTU_CODENAME-security main restricted universe multiverse\n\
deb [arch=armhf,arm64] http://ports.ubuntu.com/ubuntu-ports/ $UBUNTU_CODENAME main restricted universe multiverse\n\
deb [arch=armhf,arm64] http://ports.ubuntu.com/ubuntu-ports/ $UBUNTU_CODENAME-updates main restricted universe multiverse\n\
deb [arch=armhf,arm64] http://ports.ubuntu.com/ubuntu-ports/ $UBUNTU_CODENAME-backports main restricted universe multiverse\n\
deb [arch=armhf,arm64] http://ports.ubuntu.com/ubuntu-ports/ $UBUNTU_CODENAME-security main restricted universe multiverse"\
 > /etc/apt/sources.list

# Get crosscompilation toolchain and related packages
RUN dpkg --add-architecture $UBUNTU_ARCH
RUN apt-get update && apt-get install -yf --no-install-recommends \
        autoconf \
        automake \
        autotools-dev \
        build-essential \
        ca-certificates \
        crossbuild-essential-$UBUNTU_ARCH \
        cmake \
        curl \
        gfortran-$TARGET_TOOLCHAIN \
        git \
        gfortran \
        libtool \
        pkg-config \
        python3-dev \
        python3-pip \
        python3-venv \
        wget \
 && update-ca-certificates \
 && apt-get clean

RUN mkdir -p ${TARGET_ROOT}
RUN mkdir -p ${BUILD_ROOT}


# Crosscompile OpenBLAS
FROM build-base AS build-openblas
ARG ARCH_CFLAGS
ARG OPENBLAS_BUILD_CORES
ARG OPENBLAS_VERSION
WORKDIR ${BUILD_ROOT}
RUN git clone --depth 1 --branch ${OPENBLAS_VERSION}  https://github.com/xianyi/OpenBLAS.git
WORKDIR ${BUILD_ROOT}/OpenBLAS
RUN HAVE_NEON=1 make -j ${OPENBLAS_BUILD_CORES} TARGET=CORTEXA9 CC=$TARGET_TOOLCHAIN-gcc FC=$TARGET_TOOLCHAIN-gfortran HOSTCC=gcc
RUN make install PREFIX=$TARGET_ROOT/usr


# Crosscompile OpenCV with AXIS VDO bindings
FROM build-base AS build-opencv
ARG ARCH_CFLAGS
ARG AXIS_ARCH
ARG OPENCV_BUILD_CORES
ARG OPENCV_MODULES
ARG OPENCV_VERSION

# Get required packages for both build env and target env
RUN mkdir -p $BUILD_ROOT/opencv_deps
RUN apt-get install --reinstall --download-only -o=dir::cache=$BUILD_ROOT/opencv_deps -y -f libglib2.0-dev:$UBUNTU_ARCH libsystemd0:$UBUNTU_ARCH libgfortran5:$UBUNTU_ARCH
RUN for f in $BUILD_ROOT/opencv_deps/archives/*.deb; do dpkg -x $f $TARGET_ROOT; done
RUN for f in $BUILD_ROOT/opencv_deps/archives/*.deb; do dpkg -x $f $TARGET_ROOT/build; done
RUN apt-get install -y libglib2.0-dev libsystemd0 libglib2.0-dev:$UBUNTU_ARCH libsystemd0:$UBUNTU_ARCH
RUN cp -r /usr/lib/x86_64-linux-gnu/glib-2.0 /usr/lib/

# Get AXIS specific files for the build environment
RUN mkdir -p /usr/lib/$TARGET_TOOLCHAIN/pkgconfig
ENV PKG_CONFIG_LIBDIR=/usr/share/pkgconfig:/usr/lib/$TARGET_TOOLCHAIN/pkgconfig
COPY opencv/capaxis/$TARGET_TOOLCHAIN/include/ /usr/include/vdo
COPY opencv/capaxis/$TARGET_TOOLCHAIN/lib/ /usr/lib/$TARGET_TOOLCHAIN
COPY opencv/capaxisvdo.pc /usr/lib/$TARGET_TOOLCHAIN/pkgconfig/
COPY --from=acap-native-sdk /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/include/vdo/* /usr/include/vdo/


# Get AXIS specific files for the runtime
# The stubs added below should perhaps be separated from lib/ to avoid confusion vs full lib counterparts
COPY opencv/capaxis/$TARGET_TOOLCHAIN/stubs/ $TARGET_ROOT/build/usr/lib/
COPY opencv/capaxis/$TARGET_TOOLCHAIN/lib/ $TARGET_ROOT/build/usr/lib/
COPY --from=acap-native-sdk /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/lib/libfido* $TARGET_ROOT/build/usr/lib/
COPY --from=acap-native-sdk /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/lib/libvdo* $TARGET_ROOT/build/usr/lib/
COPY --from=acap-native-sdk /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/lib/libfido* /usr/lib/$TARGET_TOOLCHAIN/
COPY --from=acap-native-sdk /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/lib/libvdo* /usr/lib/$TARGET_TOOLCHAIN/

# Setup build directory
COPY opencv/capaxis/$TARGET_TOOLCHAIN/stubs/ $TARGET_ROOT/usr/lib/
COPY opencv/capaxis/$TARGET_TOOLCHAIN/lib/ $TARGET_ROOT/usr/lib/
COPY --from=acap-native-sdk /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/lib/libfido* $TARGET_ROOT/usr/lib/
COPY --from=acap-native-sdk /opt/axis/acapsdk/sysroots/$AXIS_ARCH/usr/lib/libvdo* $TARGET_ROOT/usr/lib/
COPY --from=build-openblas $TARGET_ROOT $TARGET_ROOT/build


# Download OpenCV
WORKDIR $BUILD_ROOT
RUN curl -fsSL https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.tar.gz | tar -xz
WORKDIR $BUILD_ROOT/opencv-${OPENCV_VERSION}
COPY opencv/cap_axis_vdo.cpp modules/videoio/src
COPY opencv/detect_axis_vdo.cmake modules/videoio/cmake
COPY opencv/axisvdo-4.5.1.patch .
RUN patch -p 1 < axisvdo-${OPENCV_VERSION}.patch

# A fix for cmake not finding our blas/lapack headers when crosscompiling
RUN sed -i 's/_find_header_file_in_dirs(OPENCV_CBLAS.*/set(OPENCV_CBLAS_H_PATH_OpenBLAS "${LAPACK_INCLUDE_DIR}\/cblas.h")/g' cmake/OpenCVFindLAPACK.cmake
RUN sed -i 's/_find_header_file_in_dirs(OPENCV_LAPACKE.*/set(OPENCV_LAPACKE_H_PATH_OpenBLAS "${LAPACK_INCLUDE_DIR}\/lapacke.h")/g' cmake/OpenCVFindLAPACK.cmake

WORKDIR $BUILD_ROOT/opencv-${OPENCV_VERSION}/build
RUN cmake -D CMAKE_TOOLCHAIN_FILE=../platforms/linux/arm-gnueabi.toolchain.cmake \
          -D CMAKE_BUILD_TYPE=RELEASE \
           # This path will contain all opencv header files
          -D CMAKE_INSTALL_PREFIX=$TARGET_ROOT/usr \
          -D INSTALL_C_EXAMPLES=OFF \
          -D CMAKE_C_FLAGS="$ARCH_CFLAGS --sysroot=$TARGET_ROOT/build" \
          -D CMAKE_CXX_FLAGS="$ARCH_CFLAGS --sysroot=$TARGET_ROOT/build" \
          -D OpenBLAS_LIB=$TARGET_ROOT/build/usr/lib/libopenblas.so \
          -D OpenBLAS_INCLUDE_DIR=$TARGET_ROOT/build/usr/include \
          -D BLAS_LIBRARIES=$TARGET_ROOT/build/usr/lib/libopenblas.so \
          # ON:
          -D BUILD_opencv_python3=OFF \
          -D WITH_TBB=ON \
          -D WITH_OPENGL=ON \
          -D BUILD_JPEG=ON \
          -D ENABLE_NEON=ON \
          -D CPU_BASELINE=NEON,VFPV3 \
          -D ENABLE_VFPV3=ON \
          -D WITH_AXIS_VDO=ON \
          -D CMAKE_SKIP_RPATH=ON \
          -D OPENCV_GENERATE_PKGCONFIG=ON \
          # ON end.
          -D WITH_OPENEXR=OFF \
          -D WITH_IPP=OFF \
          -D WITH_WEBP=OFF                  \
          -D ENABLE_PRECOMPILED_HEADERS=OFF \
          -D WITH_1394=OFF \
          -D WITH_LIBV4L=OFF \
          -D WITH_V4L=OFF \
          -D WITH_QT=OFF \
          -D WITH_GTK=OFF \
          -D WITH_FFMPEG=OFF \
          -D WITH_GSTREAMER=OFF \
          -D WITH_GSTREAMER_0_10=OFF \
          -D BUILD_LIST=$OPENCV_MODULES \
          -D BUILD_EXAMPLES=OFF \
          -D BUILD_OPENCV_DNN=OFF \
          -D BUILD_OPENCV_APPS=OFF \
          -D BUILD_DOCS=OFF \
          -D BUILD_opencv_python=OFF \
          -D BUILD_PNG=OFF \
          -D BUILD_IPP_IWD=OFF \
          -D BUILD_QUIRC=OFF \
          -D BUILD_OPENEXR=OFF \
          -D WITH_JASPER=OFF \
          -D BUILD_TIFF=OFF \
          -D BUILD_PERF_TESTS=OFF \
          -D HAVE_IPP_ICV=OFF \
          -D BUILD_IPP=OFF \
          -D BUILD_ZLIB=OFF \
          -D BUILD_TESTS=OFF \
          -D BUILD_IPP_ICV=OFF \
          -D BUILD_PROTOBUF=OFF \
          -D WITH_CUDA=OFF \
          -D HAVE_WEBP=OFF \
          ..

# Build openCV libraries and other tools
RUN make -j ${OPENCV_BUILD_CORES} install

# Remove the build directory
RUN rm -rf $TARGET_ROOT/build

# Make the header files available by creating a symlink to
# the path specified in CMAKE params
WORKDIR $TARGET_ROOT/usr/include
RUN ln -sf opencv4/opencv2 opencv2


# Package all compiled packages to their SDK directories
FROM ubuntu:${UBUNTU_VERSION} AS packages
ARG SDK_ROOT_DIR
ARG TARGET_ROOT
RUN mkdir -p $SDK_ROOT_DIR
COPY --from=build-openblas $TARGET_ROOT $SDK_ROOT_DIR/openblas
COPY --from=build-opencv $TARGET_ROOT $SDK_ROOT_DIR/opencv



# Package the "devel"-tagged image and prune some unneeded files
FROM build-base AS sdk-devel-prune
ARG SDK_ROOT_DIR
COPY --from=packages $SDK_ROOT_DIR $SDK_ROOT_DIR

# General pruning
WORKDIR $SDK_ROOT_DIR
RUN find * -type d -name 'x86_64-linux-gnu' -prune -exec rm -rf {} \;
RUN find * -type d -name 'share' -prune -exec rm -rf {} \;

# Package the "runtime"-tagged image and prune some unneeded files
FROM ubuntu:${UBUNTU_VERSION} AS sdk-runtime-prune
ARG SDK_ROOT_DIR
COPY --from=packages $SDK_ROOT_DIR $SDK_ROOT_DIR
WORKDIR $SDK_ROOT_DIR

# Prune runtime unrelated files
RUN find */usr/* -maxdepth 0 -type d -not -name 'bin' -and -not -name 'lib' -and -not -name 'sbin' -exec rm -rf {} \;
RUN find * -type f -name "*.a" -exec rm -f {} \;

# Minimal container for the devel-tagged SDK
FROM build-base AS sdk-devel
ARG ARCH_CFLAGS
ARG AXIS_ARCH
ARG BUILD_ROOT
ARG DOCKERHUB_ARCH
ARG PYTHON_VERSION
ARG SDK_ROOT_DIR
ARG TARGET_TOOLCHAIN
ARG TARGET_ROOT
ARG UBUNTU_ARCH
ARG UBUNTU_CODENAME
ARG http_proxy
ARG https_proxy

# To support DOCKER_BUILDKIT=0, base ARGs are converted to ENVs to allow propagation
ENV ARCH_CFLAGS=$ARCH_CFLAGS
ENV AXIS_ARCH=$AXIS_ARCH
ENV BUILD_ROOT=$BUILD_ROOT
ENV DOCKERHUB_ARCH=$DOCKERHUB_ARCH
ENV TARGET_TOOLCHAIN=$TARGET_TOOLCHAIN
ENV TARGET_ROOT=$TARGET_ROOT
ENV UBUNTU_ARCH=$UBUNTU_ARCH
ENV UBUNTU_CODENAME=$UBUNTU_CODENAME
COPY --from=sdk-devel-prune $SDK_ROOT_DIR $SDK_ROOT_DIR



FROM ${REPO}/${SDK}:${VERSION}-${ARCH}-ubuntu${UBUNTU_VERSION}

ARG OPENCV_VERSION=4.5.1
ARG TARGET_ROOT

# Add a sources.list file that contains the armhf repositories
# Get crosscompilation toolchain
ARG ARCH
ENV DEBIAN_FRONTEND=noninteractive
COPY sources.list /etc/apt

RUN if [ "$ARCH" = armv7hf ]; then \
        apt-get update && \
        dpkg --add-architecture armhf && \
        apt-get update && apt-get install -yf --no-install-recommends \
        ca-certificates \
        crossbuild-essential-armhf && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* ; \
    elif [ "$ARCH" = aarch64 ]; then \
        apt-get update && \
        dpkg --add-architecture arm64 && \
        apt-get update && apt-get install -yf --no-install-recommends \
        ca-certificates \
        crossbuild-essential-arm64 && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* ;\
    else \
        printf "Error: '%s' is not a valid value for the ARCH variable\n", "$ARCH"; \
        exit 1; \
    fi

RUN apt-get update && apt-get install -y -f --no-install-recommends \
    cmake \
    curl \
    pkg-config && \
    update-ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN if [ "$ARCH" = armv7hf ]; then \
        export ARCHDIR=arm-linux-gnueabihf && \
        export STRIP=arm-linux-gnueabihf-strip; \
    elif [ "$ARCH" = aarch64 ]; then \
        export ARCHDIR=g++-aarch64-linux-gnu && \
        export STRIP=aarch64-linux-gnu-strip ;\
    else \
        printf "Error: '%s' is not a valid value for the ARCH variable\n", "$ARCH"; \
        exit 1; \
    fi
ENV PKG_CONFIG_LIBDIR=/usr/share/pkgconfig:/usr/lib/$ARCHDIR/pkgconfig:/usr/lib/$ARCHDIR/pkgconfig

# Download OpenCV
WORKDIR /workspace
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /workspace/opencv-$OPENCV_VERSION/build
# Configure OpenCV
# Platform specific optimizations in the form of NEON and VFPV3 are enabled
# hadolint ignore=SC2086
ARG SDK_ROOT_DIR
COPY --from=sdk-runtime-prune $SDK_ROOT_DIR $SDK_ROOT_DIR
RUN cp -r /axis/opencv/usr/ /

RUN mkdir $TARGET_ROOT/
RUN mkdir $TARGET_ROOT/usr
RUN cp -r /axis/opencv/usr/ $TARGET_ROOT/
RUN  find / | grep "libopencv_core.so"
COPY app/ /opt/app
WORKDIR /opt/app
RUN . /opt/axis/acapsdk/environment-setup* && acap-build .
