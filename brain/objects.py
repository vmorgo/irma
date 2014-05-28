#
# Copyright (c) 2013-2014 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.database.sqlobjects import Base, Column, \
    Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True))
    scanid = Column(String)
    status = Column(Integer)
    nbfiles = Column(Integer)
    taskid = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        str_repr = (
            "Scan {0}:".format(self.scanid) +
            "\t{0} file(s)".format(self.nbfiles) +
            "\t status: '{0}'".format(self.label[self.status]) +
            "\ttaskid: '{0}'".format(self.taskid) +
            "\tuser_id: {0}\n".format(self.user_id))
        return str_repr


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    rmqvhost = Column(String)
    ftpuser = Column(String)
    quota = Column(Integer)
    scan = relationship("Scan")

    def __repr__(self):
        str_repr = (
            "User {0}:".format(self.name) +
            "\trmq_vhost: '{0}'".format(self.rmqvhost) +
            "\t ftpuser: '{0}'".format(self.ftpuser) +
            "\tquota: '{0}'\n".format(self.quota))
        return str_repr


if __name__ == "__main__":
    # create all dbs
    import config.parser as config
    import sys
    import os

    if len(sys.argv) not in (4, 5):
        print("usage: {0} <username> <rmqvhost> <ftpuser> [quota]\n"
              "      with <username> a string\n"
              "           <rmqvhost> the rmqvhost used for the frontend\n"
              "           <ftpuser> the ftpuser used by the frontend\n"
              "           [quota] the number of file scan quota\n"
              "example: {0} test1 mqfrontend frontend"
              "".format(sys.argv[0]))
        sys.exit(1)

    dirname = os.path.dirname(config.brain_config['sql_brain'].dbname)
    if not (os.path.exists(dirname) and os.path.isdir(dirname)):
        print("Error. Maybe have you forgotten to create directory {0} ?"
              "".format(dirname))
        sys.exit(1)

    # quota is in number of files (0 means disabled)
    quota = int(sys.argv) if len(sys.argv) == 5 else 0

    engine = config.brain_config['sql_brain'].engine
    dbname = config.brain_config['sql_brain'].dbname
    sql = SQLDatabase(engine + dbname)
    metadata = Base.metadata
    metadata.create_all(sql._db)
    user = User(name=sys.argv[1],
                rmqvhost=sys.argv[2],
                ftpuser=sys.argv[3],
                quota=quota)
    sql.add(user)
    sql.commit()
