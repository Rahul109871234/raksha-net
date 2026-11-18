from common .interfaces import LinkTelemetry 
W =dict (pdr =0.3 ,latency =0.25 ,history =0.2 ,anomaly =0.15 ,congestion =0.1 )

class TrustEngine :

    def __init__ (self ,alpha =0.5 ):
        self .hist ={}
        self .alpha =alpha 

    def instant (self ,t :LinkTelemetry ,anomaly :float ,hist :float )->float :
        return W ['pdr']*(1 -t .loss )+W ['latency']*max (0.0 ,1 -t .latency_ms /200 )+W ['history']*hist +W ['anomaly']*(1 -anomaly )+W ['congestion']*(1 -t .queue_depth )

    def update (self ,t :LinkTelemetry ,anomaly :float )->float :
        h =self .hist .get (t .link_id ,0.95 )
        x =self .instant (t ,anomaly ,h )
        self .hist [t .link_id ]=self .alpha *x +(1 -self .alpha )*h 
        return round (self .hist [t .link_id ],3 )