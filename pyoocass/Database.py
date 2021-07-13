import cassandra
from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, Session
from cassandra.policies import DCAwareRoundRobinPolicy, RetryPolicy
from cassandra.query import tuple_factory, BatchStatement, BatchType
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
        retries = 5
    ) -> None:
        # Initialize Attributes
        self.session = None
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
            retry_policy=CustomRetryPolicy(RETRY_MAX_ATTEMPTS=5),
            consistency_level=ConsistencyLevel.LOCAL_QUORUM,
            serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
            request_timeout=15,
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

    def connect(
        self
    ) -> bool:
        try:
            self.session = self.cluster.connect()
            if self.session is not None:
                return True
        except Exception as e:
            print(e)
            return False

    def disconnect(self) -> bool:
        self.cluster.shutdown()
        self.session = None

    def execute(
        self,
        query: str, 
        consistency_level = ConsistencyLevel.LOCAL_QUORUM
    ) -> dict:
        result_dict = {
            "action": query.split(" ")[0],
            "rows": []
        }
        try:
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