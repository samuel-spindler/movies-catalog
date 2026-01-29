// Inclusion des bibliothèques standard et de la bibliothèque cJSON
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "cjson/cJSON.h"  // Bibliothèque cJSON

// Définition des constantes pour les tailles maximales
#define MAX_FILMS 50
#define MAX_USERS 50
#define MAX_TITLE 128

// Fonction pour lire le nom de l'utilisateur cible à partir d'un fichier JSON
bool lireTarget(const char *nomFichier, char *outUser, size_t maxLen)
{
    // Ouvrir le fichier en mode lecture
    FILE *f = fopen(nomFichier, "r");
    if (!f) {
        // Si le fichier ne peut pas être ouvert : afficher un message d'erreur et retourner false
        fprintf(stderr, "Impossible d'ouvrir %s\n", nomFichier);
        return false;
    }

    // Calculer la taille du fichier pour allouer un buffer de la bonne taille 
    fseek(f, 0, SEEK_END);  // Déplacer le curseur de lecture à la fin du fichier
    long taille = ftell(f);  // Obtenir la position du curseur car position du curseur = la taille du fichier
    fseek(f, 0, SEEK_SET);   // Revenir au début du fichier

    // Allouer un buffer (zone de mémoire temporaire) de la taille du fichier en pensant à rajouter un caractère pour la fin de chaîne
    char *buffer = (char*)malloc(taille + 1);
    if (!buffer) {
        // Si l'allocation échoue -> fermer le fichier -> afficher un message d'erreur et retourner false
        fclose(f);
        fprintf(stderr, "Erreur d'allocation mémoire\n");
        return false;
    }

    // Lire le contenu du fichier dans le buffer (zone de mémoire temporaire)
    fread(buffer, 1, taille, f);
    buffer[taille] = '\0';  // Ajouter le caractère de fin de chaîne pour s'assurer que le texte est une chaîne valide

    // Fermer le fichier après lecture
    fclose(f);

    // Utiliser cJSON pour parser(transformer) le contenu JSON
    cJSON *root = cJSON_Parse(buffer);  // Parser le texte JSON
    if (!root) {
        // Si le parsing/transformation échoue -> afficher l'erreur -> libérer la mémoire et retourner false
        fprintf(stderr, "Erreur parse JSON: %s\n", cJSON_GetErrorPtr());
        free(buffer);
        return false;
    }

    // Extraire l'élément "target" du JSON qui contient le nom de l'utilisateur cible
    cJSON *user = cJSON_GetObjectItem(root, "target");
    if (!user || !cJSON_IsString(user)) {
        // Si l'élément "target" n'existe pas ou n'est pas une chaîne -> afficher une erreur -> libérer et retourner false
        fprintf(stderr, "Erreur extraction utilisateur cible\n");
        cJSON_Delete(root);
        free(buffer);
        return false;
    }

    // Copier le nom de l'utilisateur cible dans le buffer (zone de mémoire temporaire) de sortie
    strncpy(outUser, user->valuestring, maxLen - 1);
    outUser[maxLen - 1] = '\0';  // Garantir la terminaison de la chaîne

    // Libérer la mémoire allouée pour le JSON et le buffer
    cJSON_Delete(root);
    free(buffer);

    // Retourner true pour indiquer que la lecture et l'extraction ont été réussies
    return true;
}

// Définition d'une structure pour représenter un utilisateur
typedef struct {
    int   user_id;  // Identifiant unique de l'utilisateur
    char  username[64];  // Nom d'utilisateur
    int   nbFilms;  // Nombre de films notés par l'utilisateur
    char  filmsNotes[MAX_FILMS][MAX_TITLE];  // Tableau de titres de films notés
} Utilisateur;

// Fonction pour charger les utilisateurs depuis un fichier JSON
int chargerUtilisateurs(const char *filename, Utilisateur *users)
{
    // Ouvrir le fichier contenant les utilisateurs
    FILE *f = fopen(filename, "rb");
    if (!f) {
        printf("Impossible d’ouvrir %s\n", filename);
        return 0;
    }

    // Calculer la taille du fichier pour allouer un buffer
    fseek(f, 0, SEEK_END);  // Déplacer le curseur de lecture à la fin
    long sz = ftell(f);  // Obtenir la taille du fichier
    fseek(f, 0, SEEK_SET);  // Revenir au début

    // Allouer un buffer pour contenir le fichier
    char *buffer = (char*)malloc(sz + 1);
    if (!buffer) {
        fclose(f);
        printf("Erreur d’allocation mémoire\n");
        return 0;
    }

    // Lire le fichier dans le buffer
    fread(buffer, 1, sz, f);
    buffer[sz] = '\0';  // Assurer la terminaison de la chaîne
    fclose(f);

    // Parser/transformer le contenu JSON
    cJSON *root = cJSON_Parse(buffer);
    if (!root) {
        printf("Erreur parse JSON ListeUtilisateurs : %s\n", cJSON_GetErrorPtr());
        free(buffer);
        return 0;
    }

    // Vérifier que le JSON est bien un tableau
    if (!cJSON_IsArray(root)) {
        printf("Le JSON ListeUtilisateurs n’est pas un tableau.\n");
        cJSON_Delete(root);
        free(buffer);
        return 0;
    }

    // Extraire le nombre d'utilisateurs à partir du tableau JSON
    int nbUsers = cJSON_GetArraySize(root);
    if (nbUsers > MAX_USERS) nbUsers = MAX_USERS;  // Limiter à MAX_USERS utilisateurs

    // Boucle pour parcourir chaque utilisateur dans le tableau JSON
    for (int i = 0; i < nbUsers; i++) {
        cJSON *userObj = cJSON_GetArrayItem(root, i);  // Récupérer chaque objet utilisateur
        if (!userObj) continue;  // Si l'objet est NULL -> passer au suivant

        // Initialiser l'utilisateur
        Utilisateur *u = &users[i];
        u->nbFilms = 0;

        // Extraire l'ID utilisateur et le nom
        cJSON *j_id = cJSON_GetObjectItem(userObj, "user_id");
        cJSON *j_username = cJSON_GetObjectItem(userObj, "username");
        cJSON *j_notes = cJSON_GetObjectItem(userObj, "notes");

        if (j_id && cJSON_IsNumber(j_id)) {
            u->user_id = j_id->valueint;  // Récupérer l'ID utilisateur
        } else {
            u->user_id = 0;  // Valeur par défaut si l'ID n'est pas valide
        }

        // Récupérer le nom d'utilisateur
        if (j_username && cJSON_IsString(j_username)) {
            strncpy(u->username, j_username->valuestring, 63);  // Copier le nom d'utilisateur
        } else {
            strcpy(u->username, "Inconnu");  // Nom par défaut si le nom est pas trouvé
        }

        // Extraire les films notés par l'utilisateur
        if (j_notes && cJSON_IsObject(j_notes)) {
            cJSON *child = j_notes->child;  // Les films sont les éléments enfants de "notes"
            // Parcourir les films notés
            while (child) {
                if (u->nbFilms < MAX_FILMS) {
                    strncpy(u->filmsNotes[u->nbFilms], child->string, MAX_TITLE - 1);  // Stocker le titre du film
                    u->nbFilms++;  // Incrémenter le nombre de films notés
                }
                child = child->next;  // Passer au film suivant
            }
        }
    }

    // Libérer la mémoire utilisée par cJSON et le buffer
    cJSON_Delete(root);
    free(buffer);

    // Retourner le nombre d'utilisateurs chargés
    return nbUsers;
}

// Fonction pour calculer la similarité de Jaccard entre deux utilisateurs
float jaccard(const Utilisateur *A, const Utilisateur *B)
{
    int intersection_count = 0;
    // Calculer l'intersection des films notés
    for (int i = 0; i < A->nbFilms; i++) {
        const char* filmA = A->filmsNotes[i];  // Titre du film de l'utilisateur A
        // Chercher si ce film existe aussi pour l'utilisateur B
        for (int j = 0; j < B->nbFilms; j++) {
            if (strcmp(filmA, B->filmsNotes[j]) == 0) {
                intersection_count++;  // Incrémenter si le film existe dans les deux listes
                break;
            }
        }
    }

    // Calculer l'union des films notés
    int union_count = A->nbFilms + B->nbFilms - intersection_count;
    if (union_count == 0) return 0.0f;  // Eviter la division par zéro

    // Renvoyer la similarité de Jaccard (intersection / union)=formule de l'énoncé
    return (float)intersection_count / (float)union_count;
}

// Fonction pour recommander des films à un utilisateur en fonction de la similarité de Jaccard
void recommander(Utilisateur *users, int nbUsers, const char *targetName)
{
    // Trouver l'utilisateur cible dans la liste
    int idxT = -1;
    for (int i = 0; i < nbUsers; i++) {
        if (strcmp(users[i].username, targetName) == 0) {
            idxT = i;
            break;  // Utilisateur trouvé
        }
    }
    if (idxT < 0) {
        printf("Utilisateur %s introuvable dans la liste.\n", targetName);
        return;
    }

    // Calculer la similarité de Jaccard avec tous les autres utilisateurs
    float bestSim = -1.0f;
    int bestIdx = -1;
    for (int i = 0; i < nbUsers; i++) {
        if (i == idxT) continue;  // Ne pas prendre en compte l'utilisateur cible
        float sim = jaccard(&users[idxT], &users[i]);
        if (sim > bestSim) {
            bestSim = sim;
            bestIdx = i;  // Conserver l'utilisateur le plus similaire
        }
    }
    if (bestIdx < 0) {
        printf("Aucun autre utilisateur.\n");
        return;
    }

    // Afficher l'utilisateur le plus similaire
    printf("Le plus similaire à %s est %s (sim=%.3f)\n", targetName, users[bestIdx].username, bestSim);

    // Récupérer les films non vus par l'utilisateur cible
    const Utilisateur *bestUser = &users[bestIdx];
    const Utilisateur *targetU = &users[idxT];

    char recommended[MAX_FILMS][MAX_TITLE];
    int recCount = 0;

    for (int j = 0; j < bestUser->nbFilms; j++) {
        const char *titre = bestUser->filmsNotes[j];
        // Vérifier si l'utilisateur cible a déjà vu ce film
        bool dejaVu = false;
        for (int k = 0; k < targetU->nbFilms; k++) {
            if (strcmp(titre, targetU->filmsNotes[k]) == 0) {
                dejaVu = true;  // Film déjà vu par l'utilisateur cible
                break;
            }
        }
        if (!dejaVu) {
            strncpy(recommended[recCount], titre, MAX_TITLE - 1);  // Ajouter à la liste des recommandations
            recCount++;
        }
    }

    // Afficher les films recommandés
    if (recCount == 0) {
        printf("Aucune recommandation pour %s (tout déjà vu)\n", targetName);
    } else {
        printf("Recommandations pour %s:\n", targetName);
        for (int i = 0; i < recCount; i++) {
            printf(" - %s\n", recommended[i]);
        }
    }

    // Création du chemin absolu/relatif pour le fichier de sortie
    const char *cheminSortie = "Fichiers_json/recommendations.json";

    // Écrire les recommandations dans un fichier JSON
    FILE *fw = fopen(cheminSortie, "w");
    if (!fw) {
        printf("Impossible de créer %s\n", cheminSortie);
        return;
    }
    fprintf(fw, "{\n");
    fprintf(fw, "  \"target\": \"%s\",\n", targetName);
    fprintf(fw, "  \"most_similar_user\": \"%s\",\n", users[bestIdx].username);
    fprintf(fw, "  \"similarity\": %.3f,\n", bestSim);
    fprintf(fw, "  \"recommendations\": [\n");
    for (int i = 0; i < recCount; i++) {
        fprintf(fw, "    { \"titre\":\"%s\" }", recommended[i]);
        if (i < recCount - 1) fprintf(fw, ",");
        fprintf(fw, "\n");
    }
    fprintf(fw, "  ]\n}\n");

    printf("recommendations.json créé avec %d films recommandés.\n", recCount);
    fclose(fw);
}

// Fonction principale du programme
int main(void)
{
    // Lire le nom de l'utilisateur cible à partir d'un fichier JSON
    char userName[64];
    if (lireTarget("Fichiers_json/target_user.json", userName, sizeof(userName))) {
        printf("Utilisateur cible: %s\n", userName);
    } else {
        printf("Echec lors de la lecture du fichier.\n");
    }

    // Charger les utilisateurs depuis le fichier JSON
    Utilisateur users[MAX_USERS];
    int nbUsers = chargerUtilisateurs("Fichiers_json/ListeUtilisateurs.json", users);
    if (nbUsers <= 0) {
        printf("Aucun utilisateur chargé.\n");
        return 1;
    }

    // Appeler la fonction pour recommander des films
    recommander(users, nbUsers, userName);

    return 0;
}

//Commande pour compiler le programme C : gcc -o recommandation recommandation.c cjson/cJSON.c -I cjson