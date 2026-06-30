/* AmmoOS smoke — Grok16 ammoos profile compile gate */
#include <stdio.h>

int main(void)
{
    printf("ammoos-smoke ok");
#if defined(GROK16_PROFILE_AMMOOS)
    printf(" profile=ammoos");
#endif
#if defined(GROK16_BELT_2_0)
    printf(" belt_2_0");
#endif
#if defined(G16_IRONCLAD_MELD)
    printf(" ironclad");
#endif
    printf("\n");
    return 0;
}