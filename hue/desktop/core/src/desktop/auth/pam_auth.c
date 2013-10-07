#include <stdio.h>

#include <security/pam_appl.h>
#include <security/pam_misc.h>

struct pam_response *reply;

extern ssize_t getline(char **_line, size_t *_length, FILE *stream);

int conv_function(int num_msg, const struct pam_message **msg, struct pam_response **resp, void *appdata_ptr) {
  *resp = reply;
  return PAM_SUCCESS;
}

struct pam_conv conv = {
    conv_function,
    NULL
};

int main(int argc, char *argv[]) {
    int retcode = 0;
    const char *user;
    const char *service;
    pam_handle_t *pamh = NULL;
    char *password;
    size_t size = 0;

    if (argc <= 2) {
        printf("usage: pam_auth <username> <service>\n");
        exit(1);
    }

    user = argv[1];
    service =  argv[2];
    printf("pam_auth: user %s, service %s.\nType password: ", user, service);
    reply = malloc(sizeof(struct pam_response));


    getline (&password, &size, stdin);
    password[strlen(password) - 1] = 0;

    reply->resp = password;
    reply->resp_retcode = 0;

    retcode = pam_start(service, user, &conv, &pamh);
    if (retcode == PAM_SUCCESS)
        retcode = pam_authenticate(pamh, 0);

    if (retcode == PAM_SUCCESS)
        retcode = pam_acct_mgmt(pamh, 0);

    if (pam_end(pamh,retcode) != PAM_SUCCESS)
        exit(2); /*pam_end failed*/

    return retcode;
}
