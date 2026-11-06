Writing Pages
=============

The pages of a Sphinx site refer to the types of the model and to its C++
classes by name, and show its files with highlighting. This page shows each,
with the source that produces it.

NED and MSG types
-----------------

``omnetpp_neddoc``'s roles link to the pages of the NED reference, by the
short or the full name of a type:

.. code-block:: rst

   The :ned:`Network` network has a :ned:`Source`, whose :msg:`Job` messages
   are served by a :ned:`queueing node <sample.queueing.QueueingNode>`, which
   uses a :ned:`Server` like :ned:`IServer`, and connects them with
   :ned:`Link` channels.

The :ned:`Network` network has a :ned:`Source`, whose :msg:`Job` messages are
served by a :ned:`queueing node <sample.queueing.QueueingNode>`, which uses a
:ned:`Server` like :ned:`IServer`, and connects them with :ned:`Link`
channels.

C++ classes
-----------

``omnetpp_doxylink``'s ``:cppref:`` role links to the C++ API, by the name of a
class or of a member:

.. code-block:: rst

   The jobs are created by :cppref:`sample::Source`, and the
   :cppref:`sample::queueing::Server` asks
   :cppref:`sample::queueing::FifoQueue::requestJob` for the next one when
   :cppref:`isIdle <sample::queueing::Server::isIdle>`.

The jobs are created by :cppref:`sample::Source`, and the
:cppref:`sample::queueing::Server` asks
:cppref:`sample::queueing::FifoQueue::requestJob` for the next one when
:cppref:`isIdle <sample::queueing::Server::isIdle>`.

Code
----

``ned``, ``msg`` and ``ini`` code blocks are highlighted by
``omnetpp_lexers``. A page can show the files of the model itself:

.. code-block:: rst

   .. literalinclude:: ../../src/sample/queueing/QueueingNode.ned
      :language: ned

.. literalinclude:: ../../src/sample/queueing/QueueingNode.ned
   :language: ned

.. literalinclude:: ../../src/sample/Job.msg
   :language: msg

.. literalinclude:: ../../omnetpp.ini
   :language: ini
