/* KILROY Field init — minimal PID1 for ramdisk / QEMU smoke boot */
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <unistd.h>

static void mount_basic(void)
{
	mount("proc", "/proc", "proc", 0, NULL);
	mount("sysfs", "/sys", "sysfs", 0, NULL);
	mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
}

static void emit(const char *msg, size_t len)
{
	(void)write(STDOUT_FILENO, msg, len);
}

static void show_field_status(void)
{
	char buf[1024];
	ssize_t n;
	int fd;

	fd = open("/proc/kilroy_field/status", O_RDONLY);
	if (fd < 0) {
		emit("[field-init] waiting for /proc/kilroy_field\n", 44);
		return;
	}
	n = read(fd, buf, sizeof(buf) - 1);
	close(fd);
	if (n > 0)
		emit(buf, (size_t)n);
	fd = open("/proc/kilroy_field/boot", O_RDONLY);
	if (fd >= 0) {
		n = read(fd, buf, sizeof(buf) - 1);
		close(fd);
		if (n > 0)
			emit(buf, (size_t)n);
	}
	fd = open("/proc/kilroy_field/cache", O_RDONLY);
	if (fd >= 0) {
		n = read(fd, buf, sizeof(buf) - 1);
		close(fd);
		if (n > 0)
			emit(buf, (size_t)n);
	}
	fd = open("/proc/kilroy_field/direct", O_RDONLY);
	if (fd >= 0) {
		n = read(fd, buf, sizeof(buf) - 1);
		close(fd);
		if (n > 0)
			emit(buf, (size_t)n);
	}
}

int main(void)
{
	mount_basic();
	emit("KILROY Field init — Linux-compatible PID1 stub\n", 48);
	show_field_status();
	emit("[field-init] smoke OK — halting (use real rootfs for login)\n", 56);
	sync();
	reboot(RB_POWER_OFF);
	return 0;
}