{pkgs}: {
  deps = [
    pkgs.libmysqlclient
    pkgs.cacert
    pkgs.postgresql
    pkgs.openssl
  ];
}
