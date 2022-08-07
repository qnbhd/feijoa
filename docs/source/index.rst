.. feijoa documentation master file, created by
   sphinx-quickstart on Thu Aug  4 12:07:07 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to feijoa's documentation!
==================================

.. raw:: html
    :file: feijoa_logo_rtd.svg


Feijoa
===============================================

Feijoa is an automatic hyperparameter optimization software framework. It features an imperative,

Key Features
------------

* Light-weight, cross-platform
* Simple pythonic interface
* Many algorithms of optimization
* Simple customization
* Easy parallelization
* Beautiful & simple visualization

Code example
--------------

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :target: http://colab.research.google.com/github/qnbhd/feijoa/blob/main/examples/notebooks/quickstart.ipynb

.. code:: python

   import ...

   # Search Space definition

   space = SearchSpace()

   space.insert(Integer('n_neighbors', low=2, high=30))
   space.insert(Categorical('weights', choices=['uniform', 'distance']))
   space.insert(Integer('leaf_size', low=10, high=50))
   space.insert(Integer('p', low=1, high=5))

   # Or you can use
   # space = SearchSpace(
   #    Integer('n_neighbors', low=2, high=30),
   #    Categorical('weights', choices=['uniform', 'distance']),
   #    Integer('leaf_size', low=10, high=50),
   #    Integer('p', low=1, high=5),
   # )

   # Create objective function
   def objective(experiment):
       params = experiment.params

       # unpack all hyperparameters for knn __init__ method
       clf = KNeighborsClassifier(**params)

       # calc score
       score = cross_val_score(clf, X, y, scoring='roc_auc_ovr_weighted')

       return -score.mean()

   # define job
   job = create_job(search_space=space)
   # let's goooo..!
   job.do(objective, n_jobs=-1, n_trials=100)


Communication
-------------

-  `GitHub Issues <https://github.com/qnbhd/feijoa/issues>`__ for bug
   reports, feature requests and questions.

License
-------

MIT License (see `LICENSE <https://github.com/qnbhd/feijoa/blob/master/LICENSE>`__).

Authors
---------

Templin Konstantin <1qnbhd@gmail.com>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   reference/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
