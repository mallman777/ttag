if __name__ == '__main__':
    import socket
    import threading
    import sys
    import select

    ip = '127.0.0.1'
    ip = '132.163.53.127'
    port = 50000 
    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    # Send the data
    #message = 'ls -l'
    message = 'python remotecommand.py'
    while True:
        message = raw_input('Enter command to execute:')
        print 'Sending : "%s"' % message
        len_sent = s.send(message+'\n')
        # Receive a response
        if message == 'Done':
            break
        """
        while True:
            #response = s.recv(len_sent)
            response = s.recv(1024)
            if len(response)==0:
                break;
                sys.stdout.write('.')
            else:
                #sys.stdout.write('\n')
                print 'Received: "%s"' % response
        """        
        inputs = [s]
        outputs = []
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                #print s
                response = s.recv(1024)
                #print 'Received%d: %s'%(len(response),repr(response))
                print response.strip()
            if len(response)==0:
                break
            if response[-5:] == 'Done\n':
                break
        # Clean up
    s.close()

