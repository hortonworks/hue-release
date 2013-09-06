#include <stdio.h>

#include <security/pam_appl.h>
#include <security/pam_misc.h>

struct pam_response *reply;

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
    pam_handle_t *pamh = NULL;

    if (argc <= 2) {
        printf("usage: pam_auth <username> <service>\n");
        exit(1);
    }

    const char *user = argv[1];
    const char *service = argv[2];
    printf("pam_auth: user %s, service %s.\nType password: ", user, service);
    reply = malloc(sizeof(struct pam_response));

    char *password;
    size_t size = 0;

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
        exit(2); //pam_end failed

    return retcode;
}
