/* KILROY ioctl smoke test — run on booted KILROY Field OS */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include "../../include/uapi/kilroy/rtx_field.h"

int main(void)
{
	char abi[32];
	struct kilroy_field_cache cache;
	struct kilroy_field_direct direct;
	struct kilroy_field_gpu gpu;
	int fd, fail = 0;

	fd = open("/dev/kilroy_field", O_RDONLY | O_CLOEXEC);
	if (fd < 0) {
		fprintf(stderr, "kilroy-ioctl-test: open /dev/kilroy_field: %s\n",
			strerror(errno));
		return 1;
	}

	if (ioctl(fd, KILROY_IOC_GET_ABI, abi) < 0) {
		perror("GET_ABI");
		fail = 1;
	} else {
		printf("abi=%s\n", abi);
	}

	if (ioctl(fd, KILROY_IOC_GET_CACHE, &cache) < 0) {
		perror("GET_CACHE");
		fail = 1;
	} else {
		printf("cache shed=%u retention_micro=%u\n",
		       cache.shed_count, cache.retention_micro);
	}

	if (ioctl(fd, KILROY_IOC_GET_DIRECT, &direct) < 0) {
		perror("GET_DIRECT");
		fail = 1;
	} else {
		printf("direct ratio_micro=%u maps=%llu\n",
		       direct.direct_ratio_micro,
		       (unsigned long long)direct.direct_maps);
	}

	if (ioctl(fd, KILROY_IOC_GET_GPU, &gpu) < 0) {
		perror("GET_GPU");
		fail = 1;
	} else {
		printf("gpu count=%u tesla_bias_micro=%u\n",
		       gpu.gpu_count, gpu.tesla_bias_micro);
	}

	close(fd);
	return fail ? 1 : 0;
}