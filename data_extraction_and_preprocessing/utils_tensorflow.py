import tensorflow as tf

def coo_to_tensor_tensorflow(coo):
    indices = np.mat([coo.row, coo.col]).transpose()
    return tf.SparseTensor(indices, coo.data, coo.shape)

def save_tensorflow_sparse(filepath, sparse_tensor):
    sparse_ser = tf.raw_ops.SerializeSparse(sparse_indices=sparse_tensor.indices, sparse_values=sparse_tensor.values, sparse_shape=sparse_tensor.dense_shape, out_type=tf.string)
    np.save(filepath, sparse_ser.numpy())
    """
    with tf.Graph().as_default():
        sparse = coo_matrix(dense)
        sparse_indicies = list(zip(
            sparse.row.astype(np.int64).tolist(),
            sparse.col.astype(np.int64).tolist()
        ))
        type_casted = (sparse.data).astype(np.float32)
        # Make TensorFlow constants
        indices = tf.constant(sparse_indicies, name='Indices', dtype=tf.int64)
        values = tf.constant(type_casted, name='Values')
        shape = tf.constant(sparse.shape, dtype=tf.int64, name='Shape')
        # Serialize graph
        graph_def = tf.get_default_graph().as_graph_def()
        with open('sparse_tensor_data.pb', 'wb') as f:
            f.write(graph_def.SerializeToString())
    """

def load_tensorflow_sparse(filepath, sparse_tensor):
    sparse_indices, sparse_values, sparse_shape = tf.raw_ops.DeserializeSparse(tf.convert_to_tensor(np.load(filepath)), dtype=tf.string)
