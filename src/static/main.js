/**
 * Main entry for js functionality:
 * - Random TIL
 */

const TIL = {
    /**
     * Navigation util
     */
    navigation: {
        /**
         * Redirect a random TIL entry
         * Use Datasette JSON API to fetch random entry
         */
        async getRandomTIL() {
            try {
                const response = await fetch('/til.json?sql=SELECT+topic,+slug+FROM+til+ORDER+BY+RANDOM()+LIMIT+1&_shape=array');
                const data = await response.json();

                if (data && data.length > 0) {
                    const til = data[0];
                    window.location.href = `/${til.topic}/${til.slug}`;
                } else {
                    window.location.href = '/all';
                }
            } catch (error) {
                console.error('Error fetching random TIL:', error);
                window.location.href = '/all';
            }
        }
    }
};

window.TIL = TIL;

