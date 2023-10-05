from create_table import db
from sqlalchemy import REAL

class metal_inputs(db.Model):
        id= db.Column("id", db.Integer, primary_key=True)
        lat = db.Column(REAL)
        long = db.Column(REAL)
        cd= db.Column(REAL)
        cr = db.Column(REAL)
        ni = db.Column(REAL)
        pb = db.Column(REAL)
        zn = db.Column(REAL)
        cu = db.Column(REAL)
        co = db.Column(REAL)
       
        def __init__(self, lat, long, cd, cr, ni, pb, zn, cu, co):
             self.lat = lat
             self.long = long
             self.cd = cd
             self.cr = cr
             self.ni = ni
             self.pb = pb
             self.zn = zn
             self.cu = cu
             self.co = co


#Table for input values with the associated results             
class input_results(db.Model):
        id= db.Column("id", db.Integer, primary_key=True)
        lat = db.Column(REAL)
        long = db.Column(REAL)
        cd= db.Column(REAL)
        cr = db.Column(REAL)
        ni = db.Column(REAL)
        pb = db.Column(REAL)
        zn = db.Column(REAL)
        cu = db.Column(REAL)
        co = db.Column(REAL)
        predicted_mCdeg = db.Column(db.String())
        predicted_class = db.Column(db.String())
        
        def __init__(self, lat, long, cd, cr, ni, pb, zn, cu, co, predicted_mCdeg, predicted_class):
             self.lat = lat
             self.long = long
             self.cd = cd
             self.cr = cr
             self.ni = ni
             self.pb = pb
             self.zn = zn
             self.cu = cu
             self.co = co
             self.predicted_mCdeg = predicted_mCdeg
             self.predicted_class = predicted_class
             

#Table for file upload data and the associated results
class file_data(db.Model):
        id= db.Column("id", db.Integer, primary_key=True)
        lat = db.Column(REAL)
        long = db.Column(REAL)
        cd= db.Column(REAL)
        cr = db.Column(REAL)
        ni = db.Column(REAL)
        pb = db.Column(REAL)
        zn = db.Column(REAL)
        cu = db.Column(REAL)
        co = db.Column(REAL)
        predicted_mCdeg = db.Column(db.String())
        predicted_class = db.Column(db.String())

        def __init__(self, lat, long, cd, cr, ni, pb, zn, cu, co, predicted_mCdeg, predicted_class):
             self.lat = lat
             self.long = long
             self.cd = cd
             self.cr = cr
             self.ni = ni
             self.pb = pb
             self.zn = zn
             self.cu = cu
             self.co = co
             self.predicted_mCdeg = predicted_mCdeg
             self.predicted_class = predicted_class
