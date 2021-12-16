from os import name
from cassandra import ConsistencyLevel
from cassandra import query
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, Session
from cassandra.policies import DCAwareRoundRobinPolicy, RetryPolicy
from cassandra.query import SimpleStatement, tuple_factory, BatchStatement, BatchType
import json
import logging
from ssl import SSLContext, PROTOCOL_TLSv1_2 , CERT_REQUIRED
import logging
import sys

### Setup Logging ###
logger = logging.getLogger("pyoocass-Database")
log_formatter = logging.Formatter('[%(asctime)s][%(funcName)-25s][%(lineno)-3d][%(levelname)-8s] %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

## Utility Classes & Functions
class CustomRetryPolicy(RetryPolicy):
    def __init__(self, RETRY_MAX_ATTEMPTS=3):
        self.RETRY_MAX_ATTEMPTS = RETRY_MAX_ATTEMPTS
    # Handle read timeouts
    def on_read_timeout ( self, query, consistency, required_responses, received_responses, data_retrieved, retry_num):
        if retry_num <= self.RETRY_MAX_ATTEMPTS:
            return self.RETRY, consistency
        else:
            return self.RETHROW, None 
    # Handle write timeouts
    def on_write_timeout (self, query, consistency, write_type, required_responses, received_responses, retry_num):
        if retry_num <= self.RETRY_MAX_ATTEMPTS:
            return self.RETRY, consistency
        else:
            return self.RETHROW, None
    # Handle unavailable nodes
    def on_unavailable (self, query, consistency, required_replicas, alive_replicas, retry_num):
        if retry_num <= self.RETRY_MAX_ATTEMPTS:
            return self.RETRY, consistency
        else:
            return self.RETHROW, None 
    # Handle request errors
    def on_request_error (self, query, consistency, error, retry_num):
        if retry_num <= self.RETRY_MAX_ATTEMPTS:
            return self.RETRY, consistency
        else:
            return self.RETHROW, None 

class Database:
    # Setup logging
    logger = logging.getLogger(name="Database")
    # Attributes
    nodes: list
    user: str
    password: str
    cluster: Cluster
    session: Session
    auth_provider = None
    # Instance Constructor
    def __init__(
        self,
        nodes: list,
        port: int = 9042,
        user: str = "",
        password: str = "",
        cert = None,
        auth_provider = None,
        retries = 5,
        timeout = 15
    ) -> None:
        # Initialize Attributes
        self.nodes = nodes
        self.user = user
        self.password = password
        self.port = port
        self.session = None
        self.port = port
        # If SSL context is needed
        if cert is not None:
            self.ssl_context = SSLContext(PROTOCOL_TLSv1_2 )
            self.ssl_context.load_verify_locations(cert)
            self.ssl_context.verify_mode = CERT_REQUIRED
        else: 
            self.ssl_context = None
        # Check if user/password pair or auth_provider was given as parameters
        if auth_provider is None:
            if user is not None and password is not None:
                self.auth_provider = PlainTextAuthProvider(username=user, password=password)
            else:
                logger.fatal("You must provide either a user/password pair or an auth_provider object")
        else:
            self.auth_provider = auth_provider
        # define execution profile for the cluster/session
        profile = ExecutionProfile(
            load_balancing_policy=DCAwareRoundRobinPolicy(),
            retry_policy=CustomRetryPolicy(RETRY_MAX_ATTEMPTS=retries),
            consistency_level=ConsistencyLevel.LOCAL_QUORUM,
            serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
            request_timeout=timeout,
            row_factory=tuple_factory
        )
        self.cluster = Cluster(
            contact_points=nodes, 
            port=port,
            ssl_context=self.ssl_context, 
            auth_provider=self.auth_provider,
            protocol_version=4,
            execution_profiles={EXEC_PROFILE_DEFAULT: profile}
        )
        pass
    
    def __str__(self):
        json_data = {
            "nodes": self.nodes,
            "port": self.port,
            "session": None
        }
        if self.auth_provider is not None:
            json_data["auth_provider"] = type(self.auth_provider)
        if self.user is not None:
            json_data["user"] = self.user
        if self.cert is not None:
            json_data["certificate"] = self.cert
        if self.session is not None:
            json_data["session"] = self.session
            json_data["name"] = self.name
            json_data["cql_version"] = self.cql_version
            json_data["release_version"] = self.release_version
            json_data["datacenter"] = self.datacenter
            json_data["rack"] = self.rack
            json_data["native_protocol_version"] = self.native_protocol_version
        return(json_data)

    def connect(
        self
    ) -> bool:
        # Setup logging
        logger = logging.getLogger(name="Database::connect")
        logger.setLevel(logging.DEBUG)
        try:
            logger.debug("Entering try-except block")
            self.session = self.cluster.connect()
            logger.debug(f"Session after connecting: {self.session}")
            if self.session is not None:
                logger.debug("Session is not None")
                result = self.execute(query="SELECT * FROM system.local",consistency_level=ConsistencyLevel.LOCAL_ONE)
                logger.debug(result)
                self.name = result["cluster_name"]
                self.cql_version = result["cql_version"]
                self.release_version = result["release_version"]
                self.datacenter = result["datacenter"]
                self.rack = result["rack"]
                self.native_protocol_version = result["native_protocol_version"]
                return True
        except Exception as e:
            logger.debug(f"Catched exception: {e}")
            return False

    def disconnect(self) -> bool:
        self.cluster.shutdown()
        self.session = None

    def execute(
        self,
        query,
        fetch_size: int = 100,
        paging_state = None, 
        consistency_level = ConsistencyLevel.LOCAL_QUORUM
    ) -> dict:
        if type(query) is str:
            query_text = query
            query = SimpleStatement(query_text, fetch_size=fetch_size,consistency_level=consistency_level)
        else:
            query_text = query.query_string
        result_dict = {
            "action": query_text.split(" ")[0],
            "rows": []
        }
        try:
            if paging_state is not None:
                resultset = self.session.execute(query, paging_state=paging_state)
            else:
                resultset = self.session.execute(query)
            for row in resultset:
                row_dict = {}
                for i in range(len(resultset.column_names)):
                    row_dict[resultset.column_names[i]] = row[i]
                result_dict["rows"].append(row_dict)
        except Exception as e:
            logger.error(e)
        return result_dict

    def get_keyspaces(self):
        pass