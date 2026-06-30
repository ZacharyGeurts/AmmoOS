/* KILROY Field status CLI — reads /proc/kilroy_field (Linux-compatible userspace) */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int cat_path(const char *path)
{
	FILE *f;
	char buf[4096];
	size_t n;

	f = fopen(path, "r");
	if (!f) {
		fprintf(stderr, "kilroy-status: %s: %s\n", path, strerror(errno));
		return 1;
	}
	while ((n = fread(buf, 1, sizeof(buf), f)) > 0)
		fwrite(buf, 1, n, stdout);
	fclose(f);
	return 0;
}

int main(int argc, char **argv)
{
	const char *what = argc > 1 ? argv[1] : "status";
	const char *base = "/proc/kilroy_field/";
	char path[256];

	if (!strcmp(what, "help") || !strcmp(what, "-h")) {
		puts("KILROY Field status — Linux-compatible telemetry CLI");
		puts("  kilroy-status [status|boot|security|power|slots|cpu|ram|flow|cache|direct|gpu|all]");
		return 0;
	}

	if (!strcmp(what, "all")) {
		static const char *nodes[] = {
			"status", "boot", "security", "power", "slots",
			"cpu", "ram", "flow", "cache", "direct", "gpu", NULL
		};
		int err = 0;

		for (int i = 0; nodes[i]; i++) {
			snprintf(path, sizeof(path), "%s%s", base, nodes[i]);
			printf("=== %s ===\n", nodes[i]);
			err |= cat_path(path);
		}
		return err ? 1 : 0;
	}

	snprintf(path, sizeof(path), "%s%s", base, what);
	return cat_path(path) ? 1 : 0;
}