import datetime
from pyVim.task import WaitForTask
import logging


log = logging.getLogger()

class Snapshot():

	def __init__(self, virtualMachine ):
		self.vm = virtualMachine

	def get_snapshots_by_name_recursively(self,snapshots, snapname):
		snap_obj = []
		for snapshot in snapshots:
			print snapshot.name
			if snapshot.name == snapname:
				snap_obj.append(snapshot)
			else:
				snap_obj = snap_obj + self.get_snapshots_by_name_recursively(snapshot.childSnapshotList, snapname)
			#exit(1)
				
		return snap_obj


	def list_snapshots_recursively(self, snapshots):
		try:

			snapshot_data = []
			snap_text = ""
			for snapshot in snapshots:
			    snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (
			                                    snapshot.name, snapshot.description,
			                                    snapshot.createTime, snapshot.state)
			    snapshot_data.append(snapshot)
			    snapshot_data = snapshot_data + self.list_snapshots_recursively(snapshot.childSnapshotList)
			return snapshot_data
		except:
			#raise
			return False

	def create(self):
		try:
			name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");
			desc = "el dani es uto"
			task = WaitForTask(self.vm.CreateSnapshot_Task(name=name,
                              description=desc,
                              memory=False,
                              quiesce=False))
			
			log.info("Snapshot Completed.")
			
		except:
			raise
			pass 

	def delete(self, snapshot, removeChildren=False):
		try:
			log.info( "delete snapshot" )
			WaitForTask(snapshot.snapshot.RemoveSnapshot_Task(removeChildren))
		except:
			log.debug("Error irreconosible")
			raise





if __name__=='__main__':  #Cuerpo Principal
    main()