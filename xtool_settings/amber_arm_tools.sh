#!/bin/sh

# Add toolchain to PATH

# Codesourcery toolchain
# PATH=$PATH:/home/rsharm14/repository/sw/amber_arm_toolchain/bin/

# Ron's toolchain
# PATH=$PATH:/home/rsass/x-tools/arm-unknown-eabi/bin/

# bhuang2 compiled toolchain
PATH=/build/bhuang2/x-tools/arm-unknown-eabi/bin:${PATH}

# AMBER crosstool
export AMBER_CROSSTOOL=arm-unknown-eabi


